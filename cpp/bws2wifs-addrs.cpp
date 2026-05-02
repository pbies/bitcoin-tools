/*
 * bws2wifs-addrs.cpp
 *
 * Bitcoin private-key → WIF + all address types converter
 * Drop-in C++ replacement for the Python bws2wifs-addrs-vt-read-ultra-fast.py
 *
 * Dependencies (install via your package manager):
 *   libsecp256k1-dev   (secp256k1 EC operations + schnorr/taproot)
 *   libssl-dev         (SHA-256, RIPEMD-160, SHA-512)
 *   libgmp-dev         (used by secp256k1 internally)
 *
 * Build:
 *   g++ -O3 -std=c++17 -pthread bws2wifs-addrs.cpp \
 *       -lsecp256k1 -lssl -lcrypto -o bws2wifs-addrs
 *
 * Usage:
 *   ./bws2wifs-addrs [input.txt] [output.txt]
 *   (defaults to input.txt / output.txt in the current directory)
 *
 * Input format:  one private key per line, raw hex (up to 64 hex chars) OR
 *                raw binary bytes (32 bytes per line, no newline encoding needed)
 *                — matches the Python script's behaviour exactly.
 *
 * Output format (10 lines per key, blank-line-separated):
 *   <original line>
 *   <WIF uncompressed-style — base58check>
 *   <WIF compressed — via hdwallet-equivalent logic>
 *   <P2PKH  address>
 *   <P2SH   address>
 *   <P2TR   address>
 *   <P2WPKH address>
 *   <P2WPKH-in-P2SH address>
 *   <P2WSH  address>
 *   <P2WSH-in-P2SH address>
 *   <blank line>
 */

#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <queue>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include <secp256k1.h>
#include <secp256k1_extrakeys.h>  // for xonly pubkey (taproot)
#include <secp256k1_schnorrsig.h> // pulls in extrakeys too on some distros

#include <openssl/sha.h>
#include <openssl/evp.h>

// ─────────────────────────────────────────────────────────────────────────────
// Tuning constants
// ─────────────────────────────────────────────────────────────────────────────
static constexpr size_t CHUNK_LINES  = 2000;   // lines per work-block
static constexpr size_t WRITE_BUFFER = 8 << 20; // 8 MB write buffer

// ─────────────────────────────────────────────────────────────────────────────
// Base-58 alphabet (Bitcoin)
// ─────────────────────────────────────────────────────────────────────────────
static const char B58_CHARS[] =
    "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

// base58check encode: payload → base58(payload + sha256d(payload)[0..3])
static std::string base58check(const uint8_t* data, size_t len)
{
    // Double-SHA256 checksum
    uint8_t hash1[SHA256_DIGEST_LENGTH];
    uint8_t hash2[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash1);
    SHA256(hash1, SHA256_DIGEST_LENGTH, hash2);

    // Concatenate payload + 4-byte checksum
    std::vector<uint8_t> buf(data, data + len);
    buf.insert(buf.end(), hash2, hash2 + 4);

    // Count leading zeros
    size_t leading = 0;
    while (leading < buf.size() && buf[leading] == 0) ++leading;

    // Convert big-endian bytes → base-58 digits
    std::vector<uint8_t> digits;
    for (uint8_t byte : buf) {
        int carry = byte;
        for (auto it = digits.begin(); it != digits.end(); ++it) {
            carry += 256 * (*it);
            *it = carry % 58;
            carry /= 58;
        }
        while (carry) {
            digits.push_back(carry % 58);
            carry /= 58;
        }
    }

    std::string result(leading, '1');
    for (auto it = digits.rbegin(); it != digits.rend(); ++it)
        result += B58_CHARS[*it];
    return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// Hash helpers
// ─────────────────────────────────────────────────────────────────────────────

// SHA-256
static void sha256(const uint8_t* in, size_t len, uint8_t out[32])
{
    SHA256(in, len, out);
}

// RIPEMD-160 — uses the EVP API, compatible with OpenSSL 1.x and 3.x
// (the old RIPEMD160() one-shot is deprecated since OpenSSL 3.0)
static void ripemd160(const uint8_t* in, size_t len, uint8_t out[20])
{
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    const EVP_MD* md = EVP_ripemd160();
    unsigned int outlen = 20;
    EVP_DigestInit_ex(ctx, md, nullptr);
    EVP_DigestUpdate(ctx, in, len);
    EVP_DigestFinal_ex(ctx, out, &outlen);
    EVP_MD_CTX_free(ctx);
}

// Hash160 = RIPEMD160(SHA256(data))
static void hash160(const uint8_t* in, size_t len, uint8_t out[20])
{
    uint8_t h[32];
    sha256(in, len, h);
    ripemd160(h, 32, out);
}

// SHA-256 twice
static void sha256d(const uint8_t* in, size_t len, uint8_t out[32])
{
    uint8_t tmp[32];
    sha256(in, len, tmp);
    sha256(tmp, 32, out);
}

// ─────────────────────────────────────────────────────────────────────────────
// Hex helpers
// ─────────────────────────────────────────────────────────────────────────────
static std::string bytes_to_hex(const uint8_t* b, size_t n)
{
    static const char hx[] = "0123456789abcdef";
    std::string s(n * 2, '\0');
    for (size_t i = 0; i < n; ++i) {
        s[2*i]   = hx[b[i] >> 4];
        s[2*i+1] = hx[b[i] & 0xf];
    }
    return s;
}

static int hex_nibble(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

// Returns false if the string contains non-hex chars
static bool hex_to_bytes(const std::string& hex, uint8_t* out, size_t out_len)
{
    if (hex.size() != out_len * 2) return false;
    for (size_t i = 0; i < out_len; ++i) {
        int hi = hex_nibble(hex[2*i]);
        int lo = hex_nibble(hex[2*i+1]);
        if (hi < 0 || lo < 0) return false;
        out[i] = (uint8_t)((hi << 4) | lo);
    }
    return true;
}

// ─────────────────────────────────────────────────────────────────────────────
// Bech32 / Bech32m encoder (BIP-0173 / BIP-0350)
// ─────────────────────────────────────────────────────────────────────────────
static const char BECH32_CHARSET[] = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

static uint32_t bech32_polymod(const std::vector<uint8_t>& values)
{
    static const uint32_t GEN[] = {
        0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3
    };
    uint32_t chk = 1;
    for (uint8_t v : values) {
        uint8_t top = chk >> 25;
        chk = ((chk & 0x1ffffff) << 5) ^ v;
        for (int i = 0; i < 5; ++i)
            if ((top >> i) & 1) chk ^= GEN[i];
    }
    return chk;
}

// Expand hrp for checksum
static std::vector<uint8_t> bech32_hrp_expand(const std::string& hrp)
{
    std::vector<uint8_t> v;
    for (char c : hrp) v.push_back((uint8_t)c >> 5);
    v.push_back(0);
    for (char c : hrp) v.push_back((uint8_t)c & 31);
    return v;
}

// Convert 8-bit groups → 5-bit groups
static std::vector<uint8_t> convert_bits(const uint8_t* data, size_t len,
                                          int from, int to, bool pad)
{
    int acc = 0, bits = 0;
    std::vector<uint8_t> out;
    const int maxv = (1 << to) - 1;
    for (size_t i = 0; i < len; ++i) {
        acc = (acc << from) | data[i];
        bits += from;
        while (bits >= to) {
            bits -= to;
            out.push_back((acc >> bits) & maxv);
        }
    }
    if (pad && bits) out.push_back((acc << (to - bits)) & maxv);
    return out;
}

enum class Bech32Enc { BECH32, BECH32M };

static std::string bech32_encode(const std::string& hrp,
                                  const std::vector<uint8_t>& data,
                                  Bech32Enc enc)
{
    auto exp = bech32_hrp_expand(hrp);
    std::vector<uint8_t> values(exp);
    values.insert(values.end(), data.begin(), data.end());
    values.insert(values.end(), 6, 0);

    uint32_t mod = bech32_polymod(values) ^
                   (enc == Bech32Enc::BECH32M ? 0x2bc830a3u : 1u);

    std::string ret = hrp + "1";
    for (uint8_t d : data) ret += BECH32_CHARSET[d];
    for (int i = 5; i >= 0; --i)
        ret += BECH32_CHARSET[(mod >> (5 * i)) & 31];
    return ret;
}

// Encode a witness program (version + program bytes) as bech32/bech32m
static std::string segwit_addr(const std::string& hrp, int witver,
                                const uint8_t* prog, size_t prog_len)
{
    std::vector<uint8_t> enc;
    enc.push_back((uint8_t)witver);
    auto bits5 = convert_bits(prog, prog_len, 8, 5, true);
    enc.insert(enc.end(), bits5.begin(), bits5.end());

    Bech32Enc be = (witver == 0) ? Bech32Enc::BECH32 : Bech32Enc::BECH32M;
    return bech32_encode(hrp, enc, be);
}

// ─────────────────────────────────────────────────────────────────────────────
// Address derivation
// ─────────────────────────────────────────────────────────────────────────────

// P2PKH:  version 0x00, hash160(compressed-pubkey)
static std::string p2pkh(const uint8_t pub33[33])
{
    uint8_t h20[20];
    hash160(pub33, 33, h20);
    uint8_t payload[21];
    payload[0] = 0x00;
    memcpy(payload + 1, h20, 20);
    return base58check(payload, 21);
}

// P2SH: version 0x05, hash160(redeemScript)
//   redeemScript = OP_DUP OP_HASH160 <hash160(pubkey)> OP_EQUALVERIFY OP_CHECKSIG
//   (P2SH-P2PKH — matches hdwallet P2SH output)
static std::string p2sh(const uint8_t pub33[33])
{
    uint8_t h20[20];
    hash160(pub33, 33, h20);
    // redeemScript: 0x76 0xa9 0x14 <20 bytes> 0x88 0xac
    uint8_t redeem[25];
    redeem[0] = 0x76;           // OP_DUP
    redeem[1] = 0xa9;           // OP_HASH160
    redeem[2] = 0x14;           // OP_PUSH 20 bytes
    memcpy(redeem + 3, h20, 20);
    redeem[23] = 0x88;          // OP_EQUALVERIFY
    redeem[24] = 0xac;          // OP_CHECKSIG
    uint8_t script_hash[20];
    hash160(redeem, 25, script_hash);
    uint8_t payload[21];
    payload[0] = 0x05;
    memcpy(payload + 1, script_hash, 20);
    return base58check(payload, 21);
}

// P2TR (taproot): bech32m, witness v1, BIP-341 tweaked x-only key
//   tweak t = SHA256(SHA256("TapTweak") || SHA256("TapTweak") || P_x)
//   Q = P + t·G  (keypath spend with empty script tree)
static std::string p2tr(const uint8_t pub33[33],
                         secp256k1_context* ctx)
{
    secp256k1_pubkey pubkey;
    if (!secp256k1_ec_pubkey_parse(ctx, &pubkey, pub33, 33)) return "";

    // Get x-only representation of internal key P
    secp256k1_xonly_pubkey xonly;
    int parity;
    if (!secp256k1_xonly_pubkey_from_pubkey(ctx, &xonly, &parity, &pubkey))
        return "";

    uint8_t P_x[32];
    secp256k1_xonly_pubkey_serialize(ctx, P_x, &xonly);

    // Tagged hash: SHA256("TapTweak") precomputed tag hash
    // tag_hash = SHA256("TapTweak")
    static const uint8_t TAPLEAF_TAG[] = "TapTweak";
    uint8_t tag_hash[32];
    sha256(TAPLEAF_TAG, 8, tag_hash);

    // tweak = SHA256(tag_hash || tag_hash || P_x)
    uint8_t tweak_preimage[96];
    memcpy(tweak_preimage,      tag_hash, 32);
    memcpy(tweak_preimage + 32, tag_hash, 32);
    memcpy(tweak_preimage + 64, P_x,      32);
    uint8_t tweak[32];
    sha256(tweak_preimage, 96, tweak);

    // Q = P + tweak·G  via secp256k1_xonly_pubkey_tweak_add
    secp256k1_pubkey Q;
    if (!secp256k1_xonly_pubkey_tweak_add(ctx, &Q, &xonly, tweak))
        return "";

    secp256k1_xonly_pubkey xonly_Q;
    int parity_Q;
    if (!secp256k1_xonly_pubkey_from_pubkey(ctx, &xonly_Q, &parity_Q, &Q))
        return "";

    uint8_t Q_x[32];
    secp256k1_xonly_pubkey_serialize(ctx, Q_x, &xonly_Q);
    return segwit_addr("bc", 1, Q_x, 32);
}

// P2WPKH: bech32, witness v0, hash160(compressed-pubkey) [20 bytes]
static std::string p2wpkh(const uint8_t pub33[33])
{
    uint8_t h20[20];
    hash160(pub33, 33, h20);
    return segwit_addr("bc", 0, h20, 20);
}

// P2WPKH-in-P2SH: P2SH wrapping a P2WPKH witness program
//   redeemScript = OP_0 OP_PUSH20 <hash160(compressed-pubkey)>
static std::string p2wpkh_in_p2sh(const uint8_t pub33[33])
{
    uint8_t h20[20];
    hash160(pub33, 33, h20);
    // redeemScript: 0x00 0x14 <20 bytes>
    uint8_t redeem[22];
    redeem[0] = 0x00;           // OP_0
    redeem[1] = 0x14;           // OP_PUSH 20 bytes
    memcpy(redeem + 2, h20, 20);
    uint8_t script_hash[20];
    hash160(redeem, 22, script_hash);
    uint8_t payload[21];
    payload[0] = 0x05;
    memcpy(payload + 1, script_hash, 20);
    return base58check(payload, 21);
}

// P2WSH: bech32, witness v0, SHA-256(witnessScript)
//   witnessScript = OP_1 <33-byte-pubkey>  (1-of-1 multisig as example)
//   The Python hdwallet uses OP_1 <pubkey> OP_1 OP_CHECKMULTISIG
static std::string p2wsh(const uint8_t pub33[33])
{
    // witnessScript: OP_1 <33-byte pubkey> OP_1 OP_CHECKMULTISIG
    uint8_t ws[37];
    ws[0] = 0x51;           // OP_1
    ws[1] = 0x21;           // push 33 bytes
    memcpy(ws + 2, pub33, 33);
    ws[35] = 0x51;          // OP_1
    ws[36] = 0xae;          // OP_CHECKMULTISIG
    uint8_t h32[32];
    sha256(ws, 37, h32);
    return segwit_addr("bc", 0, h32, 32);
}

// P2WSH-in-P2SH: P2SH wrapping a P2WSH redeem script
static std::string p2wsh_in_p2sh(const uint8_t pub33[33])
{
    // same witnessScript as p2wsh
    uint8_t ws[37];
    ws[0] = 0x51;
    ws[1] = 0x21;
    memcpy(ws + 2, pub33, 33);
    ws[35] = 0x51;
    ws[36] = 0xae;
    uint8_t h32[32];
    sha256(ws, 37, h32);
    // redeemScript = OP_0 <32-byte-sha256>
    uint8_t redeem[34];
    redeem[0] = 0x00;
    redeem[1] = 0x20;
    memcpy(redeem + 2, h32, 32);
    uint8_t script_hash[20];
    hash160(redeem, 34, script_hash);
    uint8_t payload[21];
    payload[0] = 0x05;
    memcpy(payload + 1, script_hash, 20);
    return base58check(payload, 21);
}

// WIF: 0x80 + 32-byte-key + (optional 0x01 compressed flag)
static std::string to_wif(const uint8_t key32[32], bool compressed)
{
    uint8_t buf[34];
    buf[0] = 0x80;
    memcpy(buf + 1, key32, 32);
    size_t len = 33;
    if (compressed) { buf[33] = 0x01; len = 34; }
    return base58check(buf, len);
}

// ─────────────────────────────────────────────────────────────────────────────
// Parse a raw line into a 32-byte private key
// Mirrors the Python logic: take last 64 hex chars, zero-pad to 64.
// If the line doesn't look like hex, treat as raw 32-byte binary.
// ─────────────────────────────────────────────────────────────────────────────
static bool parse_key(const std::string& line, uint8_t key32[32])
{
    // Strip trailing whitespace
    std::string s = line;
    while (!s.empty() && (s.back() == '\r' || s.back() == '\n' || s.back() == ' '))
        s.pop_back();

    // Try hex interpretation
    bool all_hex = true;
    for (char c : s)
        if (hex_nibble(c) < 0) { all_hex = false; break; }

    if (all_hex && !s.empty()) {
        // Take at most 64 trailing hex chars
        if (s.size() > 64) s = s.substr(s.size() - 64);
        // Zero-pad to 64 on the left
        while (s.size() < 64) s = "0" + s;
        return hex_to_bytes(s, key32, 32);
    }

    // Try raw binary (exactly 32 bytes after stripping newline)
    // We already stripped \r\n above; check raw length
    if (s.size() == 32) {
        memcpy(key32, s.data(), 32);
        return true;
    }

    return false;
}

// ─────────────────────────────────────────────────────────────────────────────
// Process one block of lines; returns formatted output string
// ─────────────────────────────────────────────────────────────────────────────
static std::string process_block(const std::vector<std::string>& lines,
                                  secp256k1_context* ctx)
{
    std::string out;
    out.reserve(lines.size() * 512);

    for (const auto& line : lines) {
        uint8_t key32[32];
        if (!parse_key(line, key32)) continue;

        // Validate key with secp256k1
        if (!secp256k1_ec_seckey_verify(ctx, key32)) continue;

        // Derive compressed public key (33 bytes)
        secp256k1_pubkey pubkey;
        if (!secp256k1_ec_pubkey_create(ctx, &pubkey, key32)) continue;
        uint8_t pub33[33];
        size_t pub33_len = 33;
        secp256k1_ec_pubkey_serialize(ctx, pub33, &pub33_len,
                                       &pubkey, SECP256K1_EC_COMPRESSED);

        // Derive all outputs
        std::string wif_uncomp = to_wif(key32, false);
        std::string wif_comp   = to_wif(key32, true);
        std::string addr_p2pkh         = p2pkh(pub33);
        std::string addr_p2sh          = p2sh(pub33);
        std::string addr_p2tr          = p2tr(pub33, ctx);
        std::string addr_p2wpkh        = p2wpkh(pub33);
        std::string addr_p2wpkh_p2sh   = p2wpkh_in_p2sh(pub33);
        std::string addr_p2wsh         = p2wsh(pub33);
        std::string addr_p2wsh_p2sh    = p2wsh_in_p2sh(pub33);

        // Strip trailing newline from original line for output
        std::string raw = line;
        while (!raw.empty() && (raw.back() == '\r' || raw.back() == '\n'))
            raw.pop_back();

        out += raw + '\n';
        out += wif_uncomp   + '\n';
        out += wif_comp     + '\n';
        out += addr_p2pkh        + '\n';
        out += addr_p2sh         + '\n';
        out += addr_p2tr         + '\n';
        out += addr_p2wpkh       + '\n';
        out += addr_p2wpkh_p2sh  + '\n';
        out += addr_p2wsh        + '\n';
        out += addr_p2wsh_p2sh   + '\n';
        out += '\n';
    }
    return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// Thread-pool work queue
// ─────────────────────────────────────────────────────────────────────────────
struct WorkItem {
    std::vector<std::string> lines;
    size_t byte_count = 0;
};

class BlockQueue {
public:
    explicit BlockQueue(size_t cap) : cap_(cap) {}

    void push(WorkItem item)
    {
        std::unique_lock<std::mutex> lk(mtx_);
        not_full_.wait(lk, [this]{ return q_.size() < cap_; });
        q_.push(std::move(item));
        not_empty_.notify_one();
    }

    bool pop(WorkItem& item)
    {
        std::unique_lock<std::mutex> lk(mtx_);
        not_empty_.wait(lk, [this]{ return !q_.empty() || done_; });
        if (q_.empty()) return false;
        item = std::move(q_.front());
        q_.pop();
        not_full_.notify_one();
        return true;
    }

    void set_done()
    {
        std::unique_lock<std::mutex> lk(mtx_);
        done_ = true;
        not_empty_.notify_all();
    }

private:
    std::queue<WorkItem> q_;
    std::mutex mtx_;
    std::condition_variable not_full_, not_empty_;
    size_t cap_;
    bool done_ = false;
};

// Result queue
struct ResultItem {
    std::string text;
    size_t byte_count = 0;
};

class ResultQueue {
public:
    void push(ResultItem item)
    {
        std::unique_lock<std::mutex> lk(mtx_);
        q_.push(std::move(item));
        cv_.notify_one();
    }

    bool pop(ResultItem& item)
    {
        std::unique_lock<std::mutex> lk(mtx_);
        cv_.wait(lk, [this]{ return !q_.empty() || done_; });
        if (q_.empty()) return false;
        item = std::move(q_.front());
        q_.pop();
        return true;
    }

    void set_done()
    {
        std::unique_lock<std::mutex> lk(mtx_);
        done_ = true;
        cv_.notify_all();
    }

private:
    std::queue<ResultItem> q_;
    std::mutex mtx_;
    std::condition_variable cv_;
    bool done_ = false;
};

// ─────────────────────────────────────────────────────────────────────────────
// Progress bar (terminal)
// ─────────────────────────────────────────────────────────────────────────────
static void print_progress(size_t done, size_t total,
                             std::chrono::steady_clock::time_point t0)
{
    using namespace std::chrono;
    auto elapsed = duration_cast<seconds>(steady_clock::now() - t0).count();
    double frac = total ? (double)done / total : 0.0;
    int bar_w = 40;
    int filled = (int)(frac * bar_w);

    double speed = elapsed ? (double)done / elapsed : 0.0; // bytes/s
    std::string speed_str;
    if (speed >= 1e9)      speed_str = std::to_string((int)(speed/1e9)) + " GB/s";
    else if (speed >= 1e6) speed_str = std::to_string((int)(speed/1e6)) + " MB/s";
    else if (speed >= 1e3) speed_str = std::to_string((int)(speed/1e3)) + " KB/s";
    else                   speed_str = std::to_string((int)speed) + " B/s";

    std::cerr << "\rProcessing [";
    for (int i = 0; i < bar_w; ++i)
        std::cerr << (i < filled ? '=' : (i == filled ? '>' : ' '));
    std::cerr << "] " << std::fixed << std::setprecision(1)
              << frac*100.0 << "% " << speed_str << "   ";
    std::cerr.flush();
}

// ─────────────────────────────────────────────────────────────────────────────
// main
// ─────────────────────────────────────────────────────────────────────────────
int main(int argc, char* argv[])
{
    const char* inp_path = (argc > 1) ? argv[1] : "input.txt";
    const char* out_path = (argc > 2) ? argv[2] : "output.txt";

    // Check input file
    std::ifstream fin(inp_path, std::ios::binary | std::ios::ate);
    if (!fin) {
        std::cerr << "Error: " << inp_path << " not found!\n";
        return 1;
    }
    size_t total_bytes = (size_t)fin.tellg();
    fin.seekg(0);

    // Open output
    std::ofstream fout(out_path, std::ios::trunc);
    if (!fout) {
        std::cerr << "Error: cannot open " << out_path << " for writing\n";
        return 1;
    }

    unsigned int nworkers = std::max(1u, std::thread::hardware_concurrency());
    if (nworkers > 2) nworkers -= 2; // leave 2 cores for reader/writer
    std::cerr << "Using " << nworkers << " worker threads\n";

    // Queues
    BlockQueue  work_q(nworkers * 4);  // bounded: at most 4 blocks per worker
    ResultQueue result_q;

    // Worker threads
    std::vector<std::thread> workers;
    workers.reserve(nworkers);
    for (unsigned i = 0; i < nworkers; ++i) {
        workers.emplace_back([&work_q, &result_q]() {
            // Each thread gets its own secp256k1 context (not thread-safe to share)
            secp256k1_context* ctx =
                secp256k1_context_create(SECP256K1_CONTEXT_SIGN | SECP256K1_CONTEXT_VERIFY);
            WorkItem wi;
            while (work_q.pop(wi)) {
                std::string result = process_block(wi.lines, ctx);
                result_q.push({std::move(result), wi.byte_count});
            }
            secp256k1_context_destroy(ctx);
        });
    }

    // Writer thread
    std::atomic<size_t> bytes_done{0};
    std::thread writer([&]() {
        std::string write_buf;
        write_buf.reserve(WRITE_BUFFER);
        ResultItem ri;
        while (result_q.pop(ri)) {
            write_buf += ri.text;
            bytes_done.fetch_add(ri.byte_count, std::memory_order_relaxed);
            if (write_buf.size() >= WRITE_BUFFER) {
                fout.write(write_buf.data(), write_buf.size());
                write_buf.clear();
                write_buf.reserve(WRITE_BUFFER);
            }
        }
        if (!write_buf.empty())
            fout.write(write_buf.data(), write_buf.size());
    });

    // Reader (main thread) — feed blocks lazily
    auto t0 = std::chrono::steady_clock::now();
    {
        WorkItem wi;
        size_t block_bytes = 0;
        std::string line;
        while (std::getline(fin, line)) {
            line += '\n';
            block_bytes += line.size();
            wi.lines.push_back(line);
            if (wi.lines.size() >= CHUNK_LINES) {
                wi.byte_count = block_bytes;
                work_q.push(std::move(wi));
                wi = WorkItem{};
                block_bytes = 0;
            }
            // Progress update every ~1 MB
            if (bytes_done.load(std::memory_order_relaxed) % (1 << 20) < 4096)
                print_progress(bytes_done.load(), total_bytes, t0);
        }
        if (!wi.lines.empty()) {
            wi.byte_count = block_bytes;
            work_q.push(std::move(wi));
        }
    }

    work_q.set_done();
    for (auto& t : workers) t.join();
    result_q.set_done();
    writer.join();

    print_progress(total_bytes, total_bytes, t0);
    std::cerr << "\nDone!\a\n";
    return 0;
}
