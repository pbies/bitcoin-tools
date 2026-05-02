/*
 * bws2wifs-addrs-entropy-seed.cpp
 *
 * Input:  one line per entry — any raw bytes (binary or text).
 *
 * Each line is processed TWICE, producing two result blocks:
 *
 *   AS ENTROPY (32 bytes):
 *     raw bytes → hex string → zero-pad LEFT to 64 hex chars → 32-byte entropy
 *     → BIP39 mnemonic (24 words)
 *     → BIP39 seed via PBKDF2-HMAC-SHA512(mnemonic, "mnemonic", 2048, 64)
 *     → BIP32 master → m/44'/0'/0'/0/0 → WIF + addresses
 *
 *   AS SEED (64 bytes):
 *     raw bytes → hex string → zero-pad LEFT to 128 hex chars → 64-byte seed
 *     → BIP32 master → m/44'/0'/0'/0/0 → WIF + addresses
 *
 * Build:
 *   g++ -O3 -std=c++17 -pthread bws2wifs-addrs-entropy-seed.cpp -lsecp256k1 -lssl -lcrypto -o bws2wifs-addrs-entropy-seed
 *
 * Usage:
 *   ./bws2wifs-addrs-entropy-seed [input.txt] [output.txt]
 */

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <queue>
#include <string>
#include <thread>
#include <vector>

#include <secp256k1.h>
#include <secp256k1_extrakeys.h>
#include <secp256k1_schnorrsig.h>

#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#include "bip39_words.h"   // static const char* const BIP39_WORDS[2048]

// ─────────────────────────────────────────────────────────────────────────────
// Tuning
// ─────────────────────────────────────────────────────────────────────────────
static constexpr size_t CHUNK_LINES  = 2000;
static constexpr size_t WRITE_BUFFER = 8 << 20;

// ─────────────────────────────────────────────────────────────────────────────
// Base-58
// ─────────────────────────────────────────────────────────────────────────────
static const char B58_CHARS[] =
    "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

static std::string base58check(const uint8_t* data, size_t len)
{
    uint8_t h1[32], h2[32];
    SHA256(data, len, h1); SHA256(h1, 32, h2);
    std::vector<uint8_t> buf(data, data + len);
    buf.insert(buf.end(), h2, h2 + 4);
    size_t leading = 0;
    while (leading < buf.size() && buf[leading] == 0) ++leading;
    std::vector<uint8_t> digits;
    for (uint8_t byte : buf) {
        int carry = byte;
        for (auto& d : digits) { carry += 256*d; d = carry%58; carry /= 58; }
        while (carry) { digits.push_back(carry%58); carry /= 58; }
    }
    std::string r(leading, '1');
    for (auto it = digits.rbegin(); it != digits.rend(); ++it) r += B58_CHARS[*it];
    return r;
}

// ─────────────────────────────────────────────────────────────────────────────
// Hash helpers
// ─────────────────────────────────────────────────────────────────────────────
static void sha256h(const uint8_t* in, size_t len, uint8_t out[32])
{
    SHA256(in, len, out);
}

static void ripemd160h(const uint8_t* in, size_t len, uint8_t out[20])
{
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    unsigned int outlen = 20;
    EVP_DigestInit_ex(ctx, EVP_ripemd160(), nullptr);
    EVP_DigestUpdate(ctx, in, len);
    EVP_DigestFinal_ex(ctx, out, &outlen);
    EVP_MD_CTX_free(ctx);
}

static void hash160(const uint8_t* in, size_t len, uint8_t out[20])
{
    uint8_t h[32]; sha256h(in, len, h); ripemd160h(h, 32, out);
}

static void hmac_sha512(const uint8_t* key, size_t klen,
                         const uint8_t* data, size_t dlen,
                         uint8_t out[64])
{
    unsigned int outlen = 64;
    HMAC(EVP_sha512(), key, (int)klen, data, dlen, out, &outlen);
}

static void pbkdf2_hmac_sha512(const uint8_t* pass, size_t plen,
                                const uint8_t* salt, size_t slen,
                                int iters, uint8_t* out, size_t outlen)
{
    PKCS5_PBKDF2_HMAC((const char*)pass, (int)plen,
                       salt, (int)slen, iters,
                       EVP_sha512(), (int)outlen, out);
}

// ─────────────────────────────────────────────────────────────────────────────
// Hex helpers
// ─────────────────────────────────────────────────────────────────────────────
static int hex_nibble(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static bool hex_to_bytes(const std::string& hex, uint8_t* out, size_t out_len)
{
    if (hex.size() != out_len * 2) return false;
    for (size_t i = 0; i < out_len; ++i) {
        int hi = hex_nibble(hex[2*i]), lo = hex_nibble(hex[2*i+1]);
        if (hi < 0 || lo < 0) return false;
        out[i] = (uint8_t)((hi << 4) | lo);
    }
    return true;
}

// ─────────────────────────────────────────────────────────────────────────────
// Bech32 / Bech32m
// ─────────────────────────────────────────────────────────────────────────────
static const char BECH32_CHARSET[] = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

static uint32_t bech32_polymod(const std::vector<uint8_t>& v)
{
    static const uint32_t GEN[] = {0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3};
    uint32_t chk = 1;
    for (uint8_t x : v) {
        uint8_t top = chk >> 25;
        chk = ((chk & 0x1ffffff) << 5) ^ x;
        for (int i = 0; i < 5; ++i) if ((top>>i)&1) chk ^= GEN[i];
    }
    return chk;
}

static std::vector<uint8_t> bech32_hrp_expand(const std::string& hrp)
{
    std::vector<uint8_t> v;
    for (char c : hrp) v.push_back((uint8_t)c >> 5);
    v.push_back(0);
    for (char c : hrp) v.push_back((uint8_t)c & 31);
    return v;
}

static std::vector<uint8_t> convert_bits(const uint8_t* data, size_t len,
                                          int from, int to, bool pad)
{
    int acc = 0, bits = 0;
    std::vector<uint8_t> out;
    const int maxv = (1 << to) - 1;
    for (size_t i = 0; i < len; ++i) {
        acc = (acc << from) | data[i]; bits += from;
        while (bits >= to) { bits -= to; out.push_back((acc >> bits) & maxv); }
    }
    if (pad && bits) out.push_back((acc << (to - bits)) & maxv);
    return out;
}

enum class Bech32Enc { BECH32, BECH32M };

static std::string bech32_encode(const std::string& hrp,
                                  const std::vector<uint8_t>& data, Bech32Enc enc)
{
    auto exp = bech32_hrp_expand(hrp);
    std::vector<uint8_t> values(exp);
    values.insert(values.end(), data.begin(), data.end());
    values.insert(values.end(), 6, 0);
    uint32_t mod = bech32_polymod(values) ^ (enc == Bech32Enc::BECH32M ? 0x2bc830a3u : 1u);
    std::string ret = hrp + "1";
    for (uint8_t d : data) ret += BECH32_CHARSET[d];
    for (int i = 5; i >= 0; --i) ret += BECH32_CHARSET[(mod >> (5*i)) & 31];
    return ret;
}

static std::string segwit_addr(const std::string& hrp, int witver,
                                const uint8_t* prog, size_t prog_len)
{
    std::vector<uint8_t> enc;
    enc.push_back((uint8_t)witver);
    auto b5 = convert_bits(prog, prog_len, 8, 5, true);
    enc.insert(enc.end(), b5.begin(), b5.end());
    return bech32_encode(hrp, enc, witver == 0 ? Bech32Enc::BECH32 : Bech32Enc::BECH32M);
}

// ─────────────────────────────────────────────────────────────────────────────
// Address derivation — all verified-correct constructions
// ─────────────────────────────────────────────────────────────────────────────
static std::string make_p2pkh(const uint8_t pub33[33])
{
    uint8_t h20[20]; hash160(pub33,33,h20);
    uint8_t p[21]; p[0]=0x00; memcpy(p+1,h20,20);
    return base58check(p,21);
}

static std::string make_p2sh(const uint8_t pub33[33])
{
    // P2SH-P2PKH: redeemScript = OP_DUP OP_HASH160 <hash160> OP_EQUALVERIFY OP_CHECKSIG
    uint8_t h20[20]; hash160(pub33,33,h20);
    uint8_t redeem[25];
    redeem[0]=0x76; redeem[1]=0xa9; redeem[2]=0x14;
    memcpy(redeem+3,h20,20);
    redeem[23]=0x88; redeem[24]=0xac;
    uint8_t sh[20]; hash160(redeem,25,sh);
    uint8_t p[21]; p[0]=0x05; memcpy(p+1,sh,20);
    return base58check(p,21);
}

static std::string make_p2tr(const uint8_t pub33[33], secp256k1_context* ctx)
{
    secp256k1_pubkey pubkey;
    if (!secp256k1_ec_pubkey_parse(ctx,&pubkey,pub33,33)) return "";
    secp256k1_xonly_pubkey xonly; int parity;
    if (!secp256k1_xonly_pubkey_from_pubkey(ctx,&xonly,&parity,&pubkey)) return "";
    uint8_t P_x[32]; secp256k1_xonly_pubkey_serialize(ctx,P_x,&xonly);
    // BIP-341 keypath tweak: t = SHA256(SHA256("TapTweak") || SHA256("TapTweak") || P_x)
    static const uint8_t TAG[] = "TapTweak";
    uint8_t tag_hash[32]; sha256h(TAG,8,tag_hash);
    uint8_t pre[96];
    memcpy(pre,    tag_hash,32);
    memcpy(pre+32, tag_hash,32);
    memcpy(pre+64, P_x,     32);
    uint8_t tweak[32]; sha256h(pre,96,tweak);
    secp256k1_pubkey Q;
    if (!secp256k1_xonly_pubkey_tweak_add(ctx,&Q,&xonly,tweak)) return "";
    secp256k1_xonly_pubkey xonly_Q; int parity_Q;
    if (!secp256k1_xonly_pubkey_from_pubkey(ctx,&xonly_Q,&parity_Q,&Q)) return "";
    uint8_t Q_x[32]; secp256k1_xonly_pubkey_serialize(ctx,Q_x,&xonly_Q);
    return segwit_addr("bc",1,Q_x,32);
}

static std::string make_p2wpkh(const uint8_t pub33[33])
{
    uint8_t h20[20]; hash160(pub33,33,h20);
    return segwit_addr("bc",0,h20,20);
}

static std::string make_p2wpkh_in_p2sh(const uint8_t pub33[33])
{
    // redeemScript = OP_0 OP_PUSH20 <hash160(pubkey)>
    uint8_t h20[20]; hash160(pub33,33,h20);
    uint8_t redeem[22]; redeem[0]=0x00; redeem[1]=0x14; memcpy(redeem+2,h20,20);
    uint8_t sh[20]; hash160(redeem,22,sh);
    uint8_t p[21]; p[0]=0x05; memcpy(p+1,sh,20);
    return base58check(p,21);
}

static std::string make_p2wsh(const uint8_t pub33[33])
{
    // witnessScript = OP_1 <pubkey> OP_1 OP_CHECKMULTISIG
    uint8_t ws[37]; ws[0]=0x51; ws[1]=0x21; memcpy(ws+2,pub33,33); ws[35]=0x51; ws[36]=0xae;
    uint8_t h32[32]; sha256h(ws,37,h32);
    return segwit_addr("bc",0,h32,32);
}

static std::string make_p2wsh_in_p2sh(const uint8_t pub33[33])
{
    uint8_t ws[37]; ws[0]=0x51; ws[1]=0x21; memcpy(ws+2,pub33,33); ws[35]=0x51; ws[36]=0xae;
    uint8_t h32[32]; sha256h(ws,37,h32);
    uint8_t redeem[34]; redeem[0]=0x00; redeem[1]=0x20; memcpy(redeem+2,h32,32);
    uint8_t sh[20]; hash160(redeem,34,sh);
    uint8_t p[21]; p[0]=0x05; memcpy(p+1,sh,20);
    return base58check(p,21);
}

static std::string to_wif(const uint8_t key32[32], bool compressed)
{
    uint8_t buf[34]; buf[0]=0x80; memcpy(buf+1,key32,32);
    size_t len = 33;
    if (compressed) { buf[33]=0x01; len=34; }
    return base58check(buf,len);
}

// ─────────────────────────────────────────────────────────────────────────────
// BIP39: entropy (32 bytes) → mnemonic sentence (24 words)
// 256 entropy bits + 8 checksum bits = 264 bits → 24 × 11-bit indices
// ─────────────────────────────────────────────────────────────────────────────
static std::string entropy_to_mnemonic(const uint8_t entropy[32])
{
    uint8_t hash[32]; sha256h(entropy, 32, hash);
    uint8_t checksum = hash[0]; // top 8 bits of SHA256(entropy)

    std::string mnemonic;
    for (int w = 0; w < 24; ++w) {
        int bit_start = w * 11;
        uint32_t val = 0;
        for (int b = 0; b < 11; ++b) {
            int bit_pos = bit_start + b;
            // bits 0-255 come from entropy, bits 256-263 from checksum byte
            uint8_t byte_val = (bit_pos < 256) ? entropy[bit_pos / 8] : checksum;
            int bit_in_byte  = 7 - (bit_pos % 8);
            val = (val << 1) | ((byte_val >> bit_in_byte) & 1);
        }
        if (w > 0) mnemonic += ' ';
        mnemonic += BIP39_WORDS[val & 0x7FF];
    }
    return mnemonic;
}

// ─────────────────────────────────────────────────────────────────────────────
// BIP39: mnemonic → seed (no passphrase)
// PBKDF2-HMAC-SHA512(password=mnemonic, salt="mnemonic", iters=2048, dklen=64)
// ─────────────────────────────────────────────────────────────────────────────
static void mnemonic_to_seed(const std::string& mnemonic, uint8_t seed[64])
{
    static const uint8_t SALT[] = "mnemonic";
    pbkdf2_hmac_sha512(
        (const uint8_t*)mnemonic.data(), mnemonic.size(),
        SALT, 8,
        2048, seed, 64);
}

// ─────────────────────────────────────────────────────────────────────────────
// BIP32
// ─────────────────────────────────────────────────────────────────────────────
struct Xkey { uint8_t key[32]; uint8_t chain[32]; };

static Xkey seed_to_master(const uint8_t seed[64])
{
    static const uint8_t BSEED[] = "Bitcoin seed";
    uint8_t I[64];
    hmac_sha512(BSEED, 12, seed, 64, I);
    Xkey m; memcpy(m.key, I, 32); memcpy(m.chain, I+32, 32);
    return m;
}

// One CKD step. index >= 0x80000000 = hardened.
static bool ckd(const Xkey& parent, uint32_t index,
                secp256k1_context* ctx, Xkey& child)
{
    uint8_t data[37];
    if (index >= 0x80000000u) {
        data[0] = 0x00; memcpy(data+1, parent.key, 32);
    } else {
        secp256k1_pubkey pub;
        if (!secp256k1_ec_pubkey_create(ctx, &pub, parent.key)) return false;
        size_t len = 33;
        secp256k1_ec_pubkey_serialize(ctx, data, &len, &pub, SECP256K1_EC_COMPRESSED);
    }
    data[33] = (index>>24)&0xff; data[34] = (index>>16)&0xff;
    data[35] = (index>> 8)&0xff; data[36] = (index    )&0xff;
    uint8_t I[64];
    hmac_sha512(parent.chain, 32, data, 37, I);
    memcpy(child.key, I, 32);
    if (!secp256k1_ec_seckey_tweak_add(ctx, child.key, parent.key)) return false;
    memcpy(child.chain, I+32, 32);
    return true;
}

// Derive m/44'/0'/0'/0/0
static bool derive_m44(const Xkey& master, secp256k1_context* ctx, uint8_t key32[32])
{
    static const uint32_t PATH[] = {
        44|0x80000000u, 0|0x80000000u, 0|0x80000000u, 0, 0
    };
    Xkey cur = master, child;
    for (uint32_t idx : PATH) {
        if (!ckd(cur, idx, ctx, child)) return false;
        cur = child;
    }
    memcpy(key32, cur.key, 32);
    return true;
}

// ─────────────────────────────────────────────────────────────────────────────
// Raw line → hex string helper.
// Strips trailing \r\n, converts every remaining byte to two hex digits.
// ─────────────────────────────────────────────────────────────────────────────
static std::string line_to_hex(const std::string& line)
{
    static const char HX[] = "0123456789abcdef";
    std::string hex;
    for (unsigned char c : line) {
        if (c == '\r' || c == '\n') break;   // stop at newline
        hex += HX[c >> 4];
        hex += HX[c & 0xf];
    }
    return hex;
}

// hex → 32-byte entropy: zero-pad LEFT to 64 hex digits, take first 64.
static bool hex_to_entropy(const std::string& hex_in, uint8_t entropy[32])
{
    std::string h = hex_in;
    if (h.size() > 64) h.resize(64);
    if (h.size() < 64) h.insert(0, 64 - h.size(), '0');
    return hex_to_bytes(h, entropy, 32);
}

// hex → 64-byte seed: zero-pad LEFT to 128 hex digits, take first 128.
static bool hex_to_seed(const std::string& hex_in, uint8_t seed[64])
{
    std::string h = hex_in;
    if (h.size() > 128) h.resize(128);
    if (h.size() < 128) h.insert(0, 128 - h.size(), '0');
    return hex_to_bytes(h, seed, 64);
}

// ─────────────────────────────────────────────────────────────────────────────
// Emit one result block (raw line + WIF + addresses) into out
// ─────────────────────────────────────────────────────────────────────────────
static void emit_block(const std::string& raw, const uint8_t key32[32],
                        secp256k1_context* ctx, std::string& out)
{
    secp256k1_pubkey pubkey;
    if (!secp256k1_ec_pubkey_create(ctx, &pubkey, key32)) return;
    uint8_t pub33[33]; size_t pub33_len = 33;
    secp256k1_ec_pubkey_serialize(ctx, pub33, &pub33_len, &pubkey, SECP256K1_EC_COMPRESSED);

    out += raw                        + '\n';
    out += to_wif(key32, false)       + '\n';
    out += to_wif(key32, true)        + '\n';
    out += make_p2pkh(pub33)          + '\n';
    out += make_p2sh(pub33)           + '\n';
    out += make_p2tr(pub33, ctx)      + '\n';
    out += make_p2wpkh(pub33)         + '\n';
    out += make_p2wpkh_in_p2sh(pub33) + '\n';
    out += make_p2wsh(pub33)          + '\n';
    out += make_p2wsh_in_p2sh(pub33)  + '\n';
    out += '\n';
}

// ─────────────────────────────────────────────────────────────────────────────
// Process one block of lines — each line produces two result blocks:
//   1. treated as BIP39 entropy  (bytes→hex, pad to 64,  then entropy pipeline)
//   2. treated as BIP39 seed     (bytes→hex, pad to 128, then seed pipeline)
// ─────────────────────────────────────────────────────────────────────────────
static std::string process_block(const std::vector<std::string>& lines,
                                  secp256k1_context* ctx)
{
    std::string out;
    out.reserve(lines.size() * 1200);

    for (const auto& line : lines) {
        // Strip trailing newline for display
        std::string raw = line;
        while (!raw.empty() && (raw.back()=='\r'||raw.back()=='\n')) raw.pop_back();
        if (raw.empty()) continue;

        // Convert raw bytes to hex once
        const std::string hex = line_to_hex(line);

        // ── Block 1: as entropy ──────────────────────────────────────────────
        {
            uint8_t entropy[32];
            if (hex_to_entropy(hex, entropy)) {
                std::string mnemonic = entropy_to_mnemonic(entropy);
                uint8_t seed[64];
                mnemonic_to_seed(mnemonic, seed);
                Xkey master = seed_to_master(seed);
                uint8_t key32[32];
                if (derive_m44(master, ctx, key32) &&
                    secp256k1_ec_seckey_verify(ctx, key32))
                    emit_block(raw, key32, ctx, out);
            }
        }

        // ── Block 2: as seed ─────────────────────────────────────────────────
        {
            uint8_t seed[64];
            if (hex_to_seed(hex, seed)) {
                Xkey master = seed_to_master(seed);
                uint8_t key32[32];
                if (derive_m44(master, ctx, key32) &&
                    secp256k1_ec_seckey_verify(ctx, key32))
                    emit_block(raw, key32, ctx, out);
            }
        }
    }
    return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// Thread-pool (identical structure to vq)
// ─────────────────────────────────────────────────────────────────────────────
struct WorkItem   { std::vector<std::string> lines; size_t byte_count = 0; };
struct ResultItem { std::string text; size_t byte_count = 0; };

class BlockQueue {
public:
    explicit BlockQueue(size_t cap) : cap_(cap) {}
    void push(WorkItem item) {
        std::unique_lock<std::mutex> lk(mtx_);
        not_full_.wait(lk, [this]{ return q_.size() < cap_; });
        q_.push(std::move(item)); not_empty_.notify_one();
    }
    bool pop(WorkItem& item) {
        std::unique_lock<std::mutex> lk(mtx_);
        not_empty_.wait(lk, [this]{ return !q_.empty() || done_; });
        if (q_.empty()) return false;
        item = std::move(q_.front()); q_.pop(); not_full_.notify_one(); return true;
    }
    void set_done() { std::unique_lock<std::mutex> lk(mtx_); done_=true; not_empty_.notify_all(); }
private:
    std::queue<WorkItem> q_; std::mutex mtx_;
    std::condition_variable not_full_, not_empty_;
    size_t cap_; bool done_=false;
};

class ResultQueue {
public:
    void push(ResultItem item) {
        std::unique_lock<std::mutex> lk(mtx_); q_.push(std::move(item)); cv_.notify_one();
    }
    bool pop(ResultItem& item) {
        std::unique_lock<std::mutex> lk(mtx_);
        cv_.wait(lk, [this]{ return !q_.empty() || done_; });
        if (q_.empty()) return false;
        item = std::move(q_.front()); q_.pop(); return true;
    }
    void set_done() { std::unique_lock<std::mutex> lk(mtx_); done_=true; cv_.notify_all(); }
private:
    std::queue<ResultItem> q_; std::mutex mtx_; std::condition_variable cv_; bool done_=false;
};

// ─────────────────────────────────────────────────────────────────────────────
// Progress bar
// ─────────────────────────────────────────────────────────────────────────────
static void print_progress(size_t done, size_t total,
                             std::chrono::steady_clock::time_point t0)
{
    using namespace std::chrono;
    auto elapsed = duration_cast<seconds>(steady_clock::now()-t0).count();
    double frac = total ? (double)done/total : 0.0;
    int bar_w=40, filled=(int)(frac*bar_w);
    double speed = elapsed ? (double)done/elapsed : 0.0;
    std::string ss;
    if      (speed>=1e9) ss=std::to_string((int)(speed/1e9))+" GB/s";
    else if (speed>=1e6) ss=std::to_string((int)(speed/1e6))+" MB/s";
    else if (speed>=1e3) ss=std::to_string((int)(speed/1e3))+" KB/s";
    else                 ss=std::to_string((int)speed)+" B/s";
    std::cerr << "\rProcessing [";
    for (int i=0;i<bar_w;++i) std::cerr << (i<filled?'=':(i==filled?'>':' '));
    std::cerr << "] " << std::fixed << std::setprecision(1) << frac*100.0 << "% " << ss << "   ";
    std::cerr.flush();
}

// ─────────────────────────────────────────────────────────────────────────────
// main
// ─────────────────────────────────────────────────────────────────────────────
int main(int argc, char* argv[])
{
    const char* inp_path = (argc>1) ? argv[1] : "input.txt";
    const char* out_path = (argc>2) ? argv[2] : "output.txt";

    std::ifstream fin(inp_path, std::ios::binary|std::ios::ate);
    if (!fin) { std::cerr<<"Error: "<<inp_path<<" not found!\n"; return 1; }
    size_t total_bytes = (size_t)fin.tellg(); fin.seekg(0);

    std::ofstream fout(out_path, std::ios::trunc);
    if (!fout) { std::cerr<<"Error: cannot open "<<out_path<<"\n"; return 1; }

    unsigned int nworkers = std::max(1u, 30u); // std::thread::hardware_concurrency()
    if (nworkers > 2) nworkers -= 2;
    std::cerr << "Using " << nworkers << " worker threads\n";

    BlockQueue  work_q(nworkers*4);
    ResultQueue result_q;

    std::vector<std::thread> workers;
    workers.reserve(nworkers);
    for (unsigned i=0; i<nworkers; ++i) {
        workers.emplace_back([&work_q,&result_q](){
            secp256k1_context* ctx =
                secp256k1_context_create(SECP256K1_CONTEXT_SIGN|SECP256K1_CONTEXT_VERIFY);
            WorkItem wi;
            while (work_q.pop(wi))
                result_q.push({process_block(wi.lines, ctx), wi.byte_count});
            secp256k1_context_destroy(ctx);
        });
    }

    std::atomic<size_t> bytes_done{0};
    std::thread writer([&](){
        std::string buf; buf.reserve(WRITE_BUFFER);
        ResultItem ri;
        while (result_q.pop(ri)) {
            buf += ri.text;
            bytes_done.fetch_add(ri.byte_count, std::memory_order_relaxed);
            if (buf.size()>=WRITE_BUFFER) { fout.write(buf.data(),buf.size()); buf.clear(); buf.reserve(WRITE_BUFFER); }
        }
        if (!buf.empty()) fout.write(buf.data(),buf.size());
    });

    auto t0 = std::chrono::steady_clock::now();
    {
        WorkItem wi; size_t block_bytes=0; std::string line;
        while (std::getline(fin, line)) {
            line += '\n'; block_bytes += line.size();
            wi.lines.push_back(line);
            if (wi.lines.size()>=CHUNK_LINES) {
                wi.byte_count=block_bytes; work_q.push(std::move(wi));
                wi=WorkItem{}; block_bytes=0;
            }
            if (bytes_done.load(std::memory_order_relaxed)%(1<<20)<4096)
                print_progress(bytes_done.load(), total_bytes, t0);
        }
        if (!wi.lines.empty()) { wi.byte_count=block_bytes; work_q.push(std::move(wi)); }
    }

    work_q.set_done();
    for (auto& t : workers) t.join();
    result_q.set_done();
    writer.join();

    print_progress(total_bytes, total_bytes, t0);
    std::cerr << "\nDone!\a\n";
    return 0;
}
