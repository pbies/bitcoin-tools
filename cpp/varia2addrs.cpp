/**
 * varia2addrs.cpp  —  Bitcoin multi-address generator
 *
 * Build:
 *   g++ -std=c++20 -O2 -pthread varia2addrs.cpp -lssl -lcrypto -o varia2addrs
 *
 * Requires: OpenSSL >= 1.1  (libssl-dev)
 */

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

// OpenSSL — EVP-only, no deprecated one-shot macros
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/ec.h>
#include <openssl/bn.h>
#include <openssl/obj_mac.h>

// ============================================================================
// Byte helpers
// ============================================================================
using Bytes = std::vector<uint8_t>;

static Bytes hex_to_bytes(const std::string& hex) {
    if (hex.size() % 2 != 0) return {};
    Bytes out(hex.size() / 2);
    for (size_t i = 0; i < out.size(); ++i)
        out[i] = static_cast<uint8_t>(std::stoul(hex.substr(i * 2, 2), nullptr, 16));
    return out;
}

static std::string bytes_to_hex(const uint8_t* p, size_t n) {
    std::string s(n * 2, '0');
    static constexpr char H[] = "0123456789abcdef";
    for (size_t i = 0; i < n; ++i) {
        s[2*i]   = H[p[i] >> 4];
        s[2*i+1] = H[p[i] & 0xf];
    }
    return s;
}
static std::string bytes_to_hex(const Bytes& b) { return bytes_to_hex(b.data(), b.size()); }

// Left-zero-pad hex string to `width` hex chars
static std::string zfill_hex(const std::string& hex, size_t width) {
    if (hex.size() >= width) return hex.substr(hex.size() - width);
    return std::string(width - hex.size(), '0') + hex;
}

// ============================================================================
// 128-bit unsigned integer  —  replicate  i = int(key,16) % 2**128
// ============================================================================
struct U128 {
    uint64_t hi = 0, lo = 0;

    static U128 from_hex(const std::string& hex) {
        std::string h = hex;
        // strip leading whitespace
        while (!h.empty() && (h.front() == ' ' || h.front() == '\t')) h.erase(h.begin());
        // strip 0x prefix
        if (h.size() >= 2 && h[0] == '0' && (h[1] == 'x' || h[1] == 'X')) h.erase(0, 2);
        if (h.empty()) throw std::invalid_argument("empty hex");
        for (char c : h)
            if (!std::isxdigit((unsigned char)c)) throw std::invalid_argument("non-hex");
        // keep at most 32 hex digits (= 128 bits), implicit mod 2^128
        if (h.size() > 32) h = h.substr(h.size() - 32);
        U128 r{};
        if (h.size() > 16) {
            r.hi = std::stoull(h.substr(0, h.size() - 16), nullptr, 16);
            r.lo = std::stoull(h.substr(h.size() - 16),    nullptr, 16);
        } else {
            r.lo = std::stoull(h, nullptr, 16);
        }
        return r;
    }

    std::string to_hex() const {
        if (hi == 0) {
            std::ostringstream ss;
            ss << std::hex << lo;
            return ss.str();
        }
        std::ostringstream ss;
        ss << std::hex << hi << std::setw(16) << std::setfill('0') << lo;
        return ss.str();
    }
};

// ============================================================================
// Hash helpers — EVP so RIPEMD-160 works even in OpenSSL 3 "legacy" mode
// ============================================================================
static Bytes evp_hash(const EVP_MD* md, const uint8_t* data, size_t len) {
    unsigned char buf[EVP_MAX_MD_SIZE];
    unsigned int  olen = 0;
    EVP_MD_CTX*   ctx  = EVP_MD_CTX_new();
    if (!ctx) throw std::runtime_error("EVP_MD_CTX_new");
    EVP_DigestInit_ex(ctx, md, nullptr);
    EVP_DigestUpdate(ctx, data, len);
    EVP_DigestFinal_ex(ctx, buf, &olen);
    EVP_MD_CTX_free(ctx);
    return Bytes(buf, buf + olen);
}

static Bytes sha256v(const Bytes& d)    { return evp_hash(EVP_sha256(),    d.data(), d.size()); }
static Bytes sha256d(const Bytes& d)    { return sha256v(sha256v(d)); }
static Bytes ripemd160v(const Bytes& d) { return evp_hash(EVP_ripemd160(), d.data(), d.size()); }
static Bytes hash160(const Bytes& d)    { return ripemd160v(sha256v(d)); }

static Bytes hmac_sha512v(const Bytes& key, const Bytes& data) {
    uint8_t buf[64];
    unsigned int len = 64;
    HMAC(EVP_sha512(), key.data(), (int)key.size(),
         data.data(), data.size(), buf, &len);
    return Bytes(buf, buf + len);
}

// BIP-340 tagged hash
static Bytes tagged_hash(const std::string& tag, const Bytes& msg) {
    Bytes tb(tag.begin(), tag.end());
    Bytes th = sha256v(tb);
    Bytes pre;
    pre.insert(pre.end(), th.begin(), th.end());
    pre.insert(pre.end(), th.begin(), th.end());
    pre.insert(pre.end(), msg.begin(), msg.end());
    return sha256v(pre);
}

// ============================================================================
// Base58Check
// ============================================================================
static const char B58C[] = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

static std::string base58_encode(const Bytes& data) {
    int leading = 0;
    for (auto b : data) { if (b == 0) ++leading; else break; }
    std::vector<int> digits = {0};
    for (uint8_t byte : data) {
        int carry = byte;
        for (auto& d : digits) { carry += d * 256; d = carry % 58; carry /= 58; }
        while (carry)           { digits.push_back(carry % 58); carry /= 58; }
    }
    std::string r(leading, '1');
    for (int i = (int)digits.size() - 1; i >= 0; --i) r += B58C[digits[i]];
    return r;
}

static std::string base58check(const Bytes& payload) {
    Bytes cs = sha256d(payload);
    Bytes full = payload;
    full.insert(full.end(), cs.begin(), cs.begin() + 4);
    return base58_encode(full);
}

// ============================================================================
// Bech32 / Bech32m
// ============================================================================
static const char BECH32C[] = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

static std::vector<int> hrp_expand(const std::string& hrp) {
    std::vector<int> r;
    for (char c : hrp) r.push_back(c >> 5);
    r.push_back(0);
    for (char c : hrp) r.push_back(c & 31);
    return r;
}
static uint32_t bech32_polymod(const std::vector<int>& v) {
    static const uint32_t G[] = {0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3};
    uint32_t chk = 1;
    for (int vi : v) {
        uint8_t top = chk >> 25;
        chk = ((chk & 0x1ffffff) << 5) ^ vi;
        for (int i = 0; i < 5; ++i) if ((top >> i) & 1) chk ^= G[i];
    }
    return chk;
}
static std::string bech32_encode(const std::string& hrp,
                                  const std::vector<int>& data, bool m=false) {
    std::vector<int> combined = hrp_expand(hrp);
    combined.insert(combined.end(), data.begin(), data.end());
    combined.insert(combined.end(), 6, 0);
    uint32_t mod = bech32_polymod(combined) ^ (m ? 0x2bc830a3u : 1u);
    std::string r = hrp + "1";
    for (int d : data) r += BECH32C[d];
    for (int i = 0; i < 6; ++i) r += BECH32C[(mod >> (5*(5-i))) & 31];
    return r;
}
static std::vector<int> convertbits(const Bytes& data, int from, int to, bool pad=true) {
    int acc=0, bits=0, maxv=(1<<to)-1;
    std::vector<int> ret;
    for (auto b : data) {
        acc=(acc<<from)|b; bits+=from;
        while (bits>=to) { bits-=to; ret.push_back((acc>>bits)&maxv); }
    }
    if (pad && bits) ret.push_back((acc<<(to-bits))&maxv);
    return ret;
}
static std::string segwit_addr(const Bytes& prog, int ver) {
    std::vector<int> data = {ver};
    auto conv = convertbits(prog, 8, 5);
    data.insert(data.end(), conv.begin(), conv.end());
    return bech32_encode("bc", data, ver==1);
}

// ============================================================================
// secp256k1 — thread-local EC context (no sharing between threads)
// ============================================================================
struct ECCtx {
    EC_GROUP* group;
    BN_CTX*   ctx;
    BIGNUM*   order;
    ECCtx() {
        ctx   = BN_CTX_new();
        group = EC_GROUP_new_by_curve_name(NID_secp256k1);
        order = BN_new();
        EC_GROUP_get_order(group, order, ctx);
    }
    ~ECCtx() { BN_free(order); EC_GROUP_free(group); BN_CTX_free(ctx); }
    // non-copyable
    ECCtx(const ECCtx&) = delete;
    ECCtx& operator=(const ECCtx&) = delete;

    static ECCtx& get() { thread_local ECCtx ec; return ec; }
};

// privkey bytes (32) → compressed pubkey (33)
static Bytes privkey_to_pubkey(const Bytes& priv) {
    auto& ec = ECCtx::get();
    BIGNUM* bn = BN_bin2bn(priv.data(), (int)priv.size(), nullptr);
    EC_POINT* P = EC_POINT_new(ec.group);
    EC_POINT_mul(ec.group, P, bn, nullptr, nullptr, ec.ctx);
    size_t len = EC_POINT_point2oct(ec.group, P, POINT_CONVERSION_COMPRESSED, nullptr, 0, ec.ctx);
    Bytes out(len);
    EC_POINT_point2oct(ec.group, P, POINT_CONVERSION_COMPRESSED, out.data(), len, ec.ctx);
    EC_POINT_free(P);
    BN_free(bn);
    return out;
}

// Taproot: Q = P + H_tapTweak(x(P)) * G, return x(Q)
static Bytes taptweak_xonly(const Bytes& compressed) {
    auto& ec = ECCtx::get();
    Bytes xp(compressed.begin()+1, compressed.end()); // x-only
    Bytes tweak = tagged_hash("TapTweak", xp);

    EC_POINT* P = EC_POINT_new(ec.group);
    EC_POINT_oct2point(ec.group, P, compressed.data(), compressed.size(), ec.ctx);

    BIGNUM* t = BN_bin2bn(tweak.data(), 32, nullptr);
    EC_POINT* tG = EC_POINT_new(ec.group);
    EC_POINT_mul(ec.group, tG, t, nullptr, nullptr, ec.ctx);

    EC_POINT* Q = EC_POINT_new(ec.group);
    EC_POINT_add(ec.group, Q, P, tG, ec.ctx);

    size_t len = EC_POINT_point2oct(ec.group, Q, POINT_CONVERSION_COMPRESSED, nullptr, 0, ec.ctx);
    Bytes out(len);
    EC_POINT_point2oct(ec.group, Q, POINT_CONVERSION_COMPRESSED, out.data(), len, ec.ctx);

    EC_POINT_free(P); EC_POINT_free(tG); EC_POINT_free(Q);
    BN_free(t);
    return Bytes(out.begin()+1, out.end()); // x-only of Q
}

// ============================================================================
// Address types
// ============================================================================
static std::string addr_p2pkh(const Bytes& pub) {
    Bytes p = {0x00}; Bytes h = hash160(pub);
    p.insert(p.end(), h.begin(), h.end()); return base58check(p);
}
static std::string addr_p2wpkh(const Bytes& pub)      { return segwit_addr(hash160(pub), 0); }
static std::string addr_p2wpkh_p2sh(const Bytes& pub) {
    Bytes h = hash160(pub);
    Bytes redeem = {0x00, 0x14}; redeem.insert(redeem.end(), h.begin(), h.end());
    Bytes p = {0x05}; Bytes rh = hash160(redeem);
    p.insert(p.end(), rh.begin(), rh.end()); return base58check(p);
}
static Bytes multisig_ws(const Bytes& pub) {
    Bytes ws = {0x51};
    ws.push_back((uint8_t)pub.size());
    ws.insert(ws.end(), pub.begin(), pub.end());
    ws.push_back(0x51); ws.push_back(0xae);
    return ws;
}
static std::string addr_p2wsh(const Bytes& pub)       { return segwit_addr(sha256v(multisig_ws(pub)), 0); }
static std::string addr_p2wsh_p2sh(const Bytes& pub)  {
    Bytes ws_hash = sha256v(multisig_ws(pub));
    Bytes spk = {0x00, 0x20}; spk.insert(spk.end(), ws_hash.begin(), ws_hash.end());
    Bytes p = {0x05}; Bytes rh = hash160(spk);
    p.insert(p.end(), rh.begin(), rh.end()); return base58check(p);
}
static std::string addr_p2tr(const Bytes& pub)        { return segwit_addr(taptweak_xonly(pub), 1); }

// Compressed WIF  (starts with K or L)
static std::string privkey_to_wif_compressed(const Bytes& priv) {
    Bytes p = {0x80}; p.insert(p.end(), priv.begin(), priv.end()); p.push_back(0x01);
    return base58check(p);
}
// Uncompressed WIF  (starts with 5)
static std::string privkey_to_wif_uncompressed(const Bytes& priv) {
    Bytes p = {0x80}; p.insert(p.end(), priv.begin(), priv.end());
    return base58check(p);
}

// P2SH wrapping a P2PKH redeemScript:
//   redeemScript = OP_DUP OP_HASH160 <hash160(pubkey)> OP_EQUALVERIFY OP_CHECKSIG
// This is what hdwallet returns for wallet.address('P2SH')
static std::string addr_p2sh(const Bytes& pub) {
    Bytes h160 = hash160(pub);
    // OP_DUP=0x76 OP_HASH160=0xa9 OP_PUSHBYTES_20=0x14 <20 bytes> OP_EQUALVERIFY=0x88 OP_CHECKSIG=0xac
    Bytes redeem = {0x76, 0xa9, 0x14};
    redeem.insert(redeem.end(), h160.begin(), h160.end());
    redeem.push_back(0x88); redeem.push_back(0xac);
    Bytes p = {0x05}; Bytes rh = hash160(redeem);
    p.insert(p.end(), rh.begin(), rh.end()); return base58check(p);
}

// ============================================================================
// Wallet record
// ============================================================================
struct Wallet {
    // wif_u = uncompressed (5H...), wif_c = compressed (K.../L...)
    std::string wif_u, wif_c;
    std::string p2pkh, p2sh, p2tr, p2wpkh, p2wpkh_p2sh, p2wsh, p2wsh_p2sh;
};

static Wallet build_wallet(const Bytes& priv) {
    Bytes pub = privkey_to_pubkey(priv);
    Wallet w;
    w.wif_u       = privkey_to_wif_uncompressed(priv);
    w.wif_c       = privkey_to_wif_compressed(priv);
    w.p2pkh       = addr_p2pkh(pub);
    w.p2wpkh      = addr_p2wpkh(pub);
    w.p2sh        = addr_p2sh(pub);            // P2SH(P2PKH redeemScript)
    w.p2wpkh_p2sh = addr_p2wpkh_p2sh(pub);    // P2WPKH-in-P2SH
    w.p2wsh       = addr_p2wsh(pub);
    w.p2wsh_p2sh  = addr_p2wsh_p2sh(pub);
    w.p2tr        = addr_p2tr(pub);
    return w;
}

// ============================================================================
// BIP-32 key derivation  (m / 84' / 0' / 0' / 0 / 0)
// ============================================================================
struct ExtKey { Bytes key, chain; };

static ExtKey master_from_seed(const Bytes& seed) {
    static const Bytes BSEED={'B','i','t','c','o','i','n',' ','s','e','e','d'};
    Bytes I = hmac_sha512v(BSEED, seed);
    return { Bytes(I.begin(), I.begin()+32), Bytes(I.begin()+32, I.end()) };
}

static ExtKey child_key(const ExtKey& par, uint32_t idx) {
    auto& ec = ECCtx::get();
    Bytes data;
    if (idx >= 0x80000000u) {
        data.push_back(0x00);
        data.insert(data.end(), par.key.begin(), par.key.end());
    } else {
        Bytes pub = privkey_to_pubkey(par.key);
        data.insert(data.end(), pub.begin(), pub.end());
    }
    data.push_back((idx>>24)&0xFF); data.push_back((idx>>16)&0xFF);
    data.push_back((idx>> 8)&0xFF); data.push_back( idx     &0xFF);

    Bytes I = hmac_sha512v(par.chain, data);

    BIGNUM* il = BN_bin2bn(I.data(), 32, nullptr);
    BIGNUM* pk = BN_bin2bn(par.key.data(), (int)par.key.size(), nullptr);
    BIGNUM* ck = BN_new();
    BN_mod_add(ck, il, pk, ec.order, ec.ctx);

    ExtKey child;
    child.key.assign(32, 0);
    int nb = BN_num_bytes(ck);
    BN_bn2bin(ck, child.key.data() + 32 - nb);
    child.chain = Bytes(I.begin()+32, I.end());

    BN_free(il); BN_free(pk); BN_free(ck);
    return child;
}

static ExtKey bip84_leaf(const ExtKey& master) {
    ExtKey k = master;
    for (uint32_t i : {0x80000054u, 0x80000000u, 0x80000000u, 0u, 0u})
        k = child_key(k, i);
    return k;
}

// ============================================================================
// Four wallet variants matching the Python script
// ============================================================================
static std::optional<Wallet> variant_from_seed(const std::string& hex) {
    Bytes seed = hex_to_bytes(hex);
    if (seed.empty()) return std::nullopt;
    auto leaf = bip84_leaf(master_from_seed(seed));
    if (leaf.key.size() != 32) return std::nullopt;
    return build_wallet(leaf.key);
}

static std::optional<Wallet> variant_from_privkey(const std::string& hex) {
    Bytes priv = hex_to_bytes(hex);
    if (priv.size() != 32) return std::nullopt;
    return build_wallet(priv);
}

static std::optional<Wallet> variant_from_entropy(const std::string& hex) {
    Bytes entropy = hex_to_bytes(hex);
    if (entropy.empty()) return std::nullopt;
    static const uint8_t SALT[] = {'m','n','e','m','o','n','i','c'};
    Bytes seed(64);
    PKCS5_PBKDF2_HMAC(
        reinterpret_cast<const char*>(entropy.data()), (int)entropy.size(),
        SALT, sizeof(SALT), 2048, EVP_sha512(), 64, seed.data());
    auto leaf = bip84_leaf(master_from_seed(seed));
    if (leaf.key.size() != 32) return std::nullopt;
    return build_wallet(leaf.key);
}

static std::optional<Wallet> variant_from_xprv(const std::string& hex) {
    return variant_from_seed(hex); // same derivation path
}

// ============================================================================
// Core per-key function  (called from worker threads, fully re-entrant)
// ============================================================================
static std::string process_key(const std::string& raw) {
    size_t a = raw.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return "";
    size_t b = raw.find_last_not_of(" \t\r\n");
    const std::string key = raw.substr(a, b - a + 1);

    U128 i;
    try { i = U128::from_hex(key); }
    catch (...) { return ""; }

    const std::string hex_i = i.to_hex();
    const std::string s1 = zfill_hex(hex_i, 128); // 64-byte seed
    const std::string s2 = zfill_hex(hex_i,  64); // 32-byte privkey
    const std::string s3 = zfill_hex(hex_i,  32); // 16-byte entropy
    const std::string s4 = s1;                     // xprv (same)

    using Factory = std::optional<Wallet>(const std::string&);
    Factory* factories[4] = {
        variant_from_seed,
        variant_from_privkey,
        variant_from_entropy,
        variant_from_xprv,
    };
    const std::string* args[4] = { &s1, &s2, &s3, &s4 };

    std::string result;
    result.reserve(512);
    for (int f = 0; f < 4; ++f) {
        try {
            auto opt = factories[f](*args[f]);
            if (!opt) continue;
            const auto& w = *opt;
            result += key           + "\n"
                    + w.wif_u       + "\n"   // uncompressed WIF (5H...)
                    + w.wif_c       + "\n"   // compressed WIF   (K/L...)
                    + w.p2pkh       + "\n"
                    + w.p2sh        + "\n"
                    + w.p2tr        + "\n"
                    + w.p2wpkh      + "\n"
                    + w.p2wpkh_p2sh + "\n"
                    + w.p2wsh       + "\n"
                    + w.p2wsh_p2sh  + "\n\n";
        } catch (...) { continue; }
    }
    return result;
}

// ============================================================================
// Thread pool  (back-pressure: submit blocks when queue is full)
// ============================================================================
class ThreadPool {
public:
    explicit ThreadPool(unsigned n) : stop_(false), active_(0) {
        workers_.reserve(n);
        for (unsigned i = 0; i < n; ++i)
            workers_.emplace_back([this]{ loop(); });
    }
    ~ThreadPool() {
        { std::lock_guard<std::mutex> lk(mtx_); stop_ = true; }
        cv_work_.notify_all();
        for (auto& t : workers_) if (t.joinable()) t.join();
    }

    void submit(std::string line, std::function<void(std::string)> cb) {
        std::unique_lock<std::mutex> lk(mtx_);
        cv_space_.wait(lk, [&]{ return queue_.size() < CAP || stop_; });
        queue_.push_back({std::move(line), std::move(cb)});
        lk.unlock();
        cv_work_.notify_one();
    }

    void drain() {
        std::unique_lock<std::mutex> lk(mtx_);
        cv_done_.wait(lk, [&]{ return queue_.empty() && active_ == 0; });
    }

private:
    static constexpr size_t CAP = 2048;

    struct Task { std::string line; std::function<void(std::string)> cb; };

    void loop() {
        for (;;) {
            Task t;
            {
                std::unique_lock<std::mutex> lk(mtx_);
                cv_work_.wait(lk, [&]{ return !queue_.empty() || stop_; });
                if (queue_.empty()) return;  // stop_ set
                t = std::move(queue_.front());
                queue_.pop_front();
                ++active_;
            }
            cv_space_.notify_one();          // freed a slot

            std::string res = process_key(t.line);
            t.cb(std::move(res));

            {
                std::lock_guard<std::mutex> lk(mtx_);
                --active_;
            }
            cv_done_.notify_all();
        }
    }

    std::vector<std::thread>  workers_;
    std::deque<Task>          queue_;
    std::mutex                mtx_;
    std::condition_variable   cv_work_, cv_space_, cv_done_;
    bool                      stop_;
    unsigned                  active_;
};

// ============================================================================
// Progress bar (ANSI \r, throttled to every 512 ticks to minimise lock contention)
// ============================================================================
class ProgressBar {
public:
    explicit ProgressBar(uint64_t total, int w=50)
        : total_(total), w_(w), done_(0), t0_(std::chrono::steady_clock::now()) {}

    void tick() {
        uint64_t cur = ++done_;
        if (cur & 0x1FF) return;            // redraw every 512
        std::lock_guard<std::mutex> lk(mtx_);
        draw(cur);
    }
    void finish() {
        std::lock_guard<std::mutex> lk(mtx_);
        draw(done_.load()); std::cerr << "\n";
    }
private:
    void draw(uint64_t cur) {
        double frac   = total_ ? (double)cur/(double)total_ : 0.0;
        int    filled = (int)(frac*w_);
        double elapsed= std::chrono::duration<double>(
                            std::chrono::steady_clock::now()-t0_).count();
        double rate   = elapsed>0 ? cur/elapsed : 0;
        double eta    = (rate>0 && cur<total_) ? (total_-cur)/rate : 0;
        std::ostringstream ss;
        ss << "\r[";
        for (int i=0;i<w_;++i) ss<<(i<filled?'#':'-');
        ss << "] " << std::fixed << std::setprecision(1) << frac*100 << "%  "
           << cur << "/" << total_
           << "  " << std::setprecision(0) << rate << " key/s"
           << "  ETA " << (int)eta << "s   ";
        std::cerr << ss.str() << std::flush;
    }
    const uint64_t total_; const int w_;
    std::atomic<uint64_t> done_;
    std::chrono::steady_clock::time_point t0_;
    std::mutex mtx_;
};

// ============================================================================
// Fast streaming line counter (no heap per line)
// ============================================================================
static uint64_t count_lines(const char* path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return 0;
    uint64_t n = 0;
    char buf[1<<20];
    while (f.read(buf, sizeof buf) || f.gcount())
        for (std::streamsize i=0; i<f.gcount(); ++i)
            if (buf[i]=='\n') ++n;
    return n;
}

// ============================================================================
// main
// ============================================================================
int main(int argc, char** argv) {
    const char* INPUT  = argc > 1 ? argv[1] : "input.txt";
    const char* OUTPUT = argc > 2 ? argv[2] : "output.txt";

    { std::ifstream p(INPUT); if (!p) { std::cerr<<"Error: cannot open "<<INPUT<<"\n"; return 1; } }

    std::cerr << "Counting lines... " << std::flush;
    uint64_t total = count_lines(INPUT);
    std::cerr << total << "\n";
    if (total == 0) { std::cerr << "Nothing to process.\n"; return 0; }

    { std::ofstream _(OUTPUT, std::ios::trunc); } // truncate

    unsigned nw = std::max(1u, std::thread::hardware_concurrency() - 2u);
    if (nw == 0) nw = 4;
    std::cerr << "Workers: " << nw << "\n";

    ProgressBar        bar(total);
    std::mutex         out_mtx;
    std::vector<std::string> wbuf;
    wbuf.reserve(128);
    std::ofstream outfile(OUTPUT, std::ios::app);

    auto flush_wbuf = [&]{
        for (auto& s : wbuf) outfile.write(s.data(), (std::streamsize)s.size());
        wbuf.clear();
        outfile.flush();
    };

    {
        ThreadPool pool(nw);
        std::ifstream infile(INPUT);
        std::string line;

        while (std::getline(infile, line)) {
            pool.submit(line, [&](std::string res) {
                bar.tick();
                if (res.empty()) return;
                std::lock_guard<std::mutex> lk(out_mtx);
                wbuf.push_back(std::move(res));
                if (wbuf.size() >= 64) flush_wbuf();
            });
        }
        pool.drain();
    }

    { std::lock_guard<std::mutex> lk(out_mtx); flush_wbuf(); }
    bar.finish();
    std::cerr << '\a';
    std::cout << "Done. Results in " << OUTPUT << "\n";
    return 0;
}
