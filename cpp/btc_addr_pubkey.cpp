// btc_addr_pubkey.cpp
//
// Extracts Bitcoin address + public key pairs from two sources:
//
//   SOURCE 1 — blk*.dat (blocks directory)
//     Scans P2PKH scriptSig fields in transaction inputs.
//     Pattern: <push><DER sig><push><pubkey 33 or 65 bytes>
//     Covers all historical P2PKH spends.
//
//   SOURCE 2 — chainstate (LevelDB)
//     Reads current UTXO set for P2PK outputs (script types 2/3/4/5).
//     These contain the raw pubkey; no spending needed.
//     P2PKH UTXOs (types 0/1) store hash160 only — skipped here,
//     they will appear in blk*.dat when spent.
//
// Output format (one pair per line, TAB separated):
//   <address>\t<pubkey_hex>
//
// Build:
//   g++ -O2 -std=c++17 btc_addr_pubkey.cpp -lssl -lcrypto -lleveldb -o btc_addr_pubkey
//
// Usage:
//   ./btc_addr_pubkey --blocks  <blocks_dir>     [output_file]
//   ./btc_addr_pubkey --chain   <chainstate_dir>  [output_file]
//   ./btc_addr_pubkey --both    <bitcoin_datadir> [output_file]
//
//   --both expects the root datadir containing both blocks/ and chainstate/
//
// Output is appended if output_file exists. Bitcoin Core must be stopped
// before reading chainstate. blocks/ can be read while Core is running
// (files already written are complete and immutable).

#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <stdexcept>
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <leveldb/db.h>
#include <leveldb/options.h>

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
static const uint32_t MAINNET_MAGIC = 0xD9B4BEF9;
static const uint32_t TESTNET_MAGIC = 0x0709110B;
static const uint32_t SIGNET_MAGIC  = 0x40CF030A;

// ---------------------------------------------------------------------------
// Reader
// ---------------------------------------------------------------------------
struct Reader {
	const uint8_t *p;
	const uint8_t *end;

	Reader(const uint8_t *data, size_t len) : p(data), end(data + len) {}

	size_t remaining() const { return (size_t)(end - p); }

	void require(size_t n) const {
		if (remaining() < n) throw std::runtime_error("truncated");
	}

	uint8_t  u8()  { require(1); return *p++; }
	uint16_t u16() { require(2); uint16_t v=(uint16_t)p[0]|((uint16_t)p[1]<<8); p+=2; return v; }
	uint32_t u32() { require(4); uint32_t v=(uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24); p+=4; return v; }
	uint64_t u64() { require(8); uint64_t v=0; for(int i=0;i<8;i++) v|=((uint64_t)p[i]<<(8*i)); p+=8; return v; }

	uint64_t varint() {
		uint8_t b=u8();
		if (b<0xfd) return b;
		if (b==0xfd) return u16();
		if (b==0xfe) return (uint64_t)u32();
		return u64();
	}

	// chainstate-style varint (7-bit groups, continuation bit = 0x80, value+1 on each group except last)
	uint64_t varint_cs() {
		uint64_t n=0;
		while (p<end) {
			uint8_t b=*p++;
			n=(n<<7)|(b&0x7f);
			if (b&0x80) n++; else return n;
		}
		throw std::runtime_error("cs varint truncated");
	}

	std::vector<uint8_t> read(size_t n) {
		require(n); std::vector<uint8_t> v(p,p+n); p+=n; return v;
	}

	void skip(size_t n) { require(n); p+=n; }
};

// ---------------------------------------------------------------------------
// Crypto helpers
// ---------------------------------------------------------------------------
static void dsha256(const uint8_t *data, size_t len, uint8_t out[32])
{
	uint8_t tmp[32];
	SHA256(data, len, tmp);
	SHA256(tmp, 32, out);
}

static void hash160(const uint8_t *data, size_t len, uint8_t out[20])
{
	uint8_t sha[32];
	SHA256(data, len, sha);
	EVP_MD_CTX *ctx = EVP_MD_CTX_new();
	unsigned int ol = 20;
	EVP_DigestInit_ex(ctx, EVP_ripemd160(), nullptr);
	EVP_DigestUpdate(ctx, sha, 32);
	EVP_DigestFinal_ex(ctx, out, &ol);
	EVP_MD_CTX_free(ctx);
}

// ---------------------------------------------------------------------------
// Base58Check
// ---------------------------------------------------------------------------
static const char *B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

static std::string base58check(uint8_t version, const uint8_t *payload, size_t plen)
{
	std::vector<uint8_t> buf(1 + plen + 4);
	buf[0] = version;
	memcpy(buf.data() + 1, payload, plen);
	uint8_t chk[32];
	dsha256(buf.data(), 1 + plen, chk);
	memcpy(buf.data() + 1 + plen, chk, 4);

	size_t total = 1 + plen + 4;
	size_t lz = 0;
	while (lz < total && buf[lz] == 0) lz++;

	std::vector<uint8_t> digits(total * 136 / 100 + 1, 0);
	size_t dl = 0;
	for (size_t i = 0; i < total; i++) {
		uint32_t carry = buf[i];
		for (size_t j = 0; j < dl; j++) {
			carry += (uint32_t)digits[j] << 8;
			digits[j] = carry % 58;
			carry /= 58;
		}
		while (carry) { digits[dl++] = carry % 58; carry /= 58; }
	}
	if (!dl) dl = 1;

	std::string result(lz, '1');
	for (size_t i = dl; i-- > 0;) result += B58[digits[i]];
	return result;
}

// ---------------------------------------------------------------------------
// Hex
// ---------------------------------------------------------------------------
static std::string to_hex(const uint8_t *data, size_t len)
{
	static const char *hc = "0123456789abcdef";
	std::string s(len * 2, '0');
	for (size_t i = 0; i < len; i++) {
		s[2*i]   = hc[data[i] >> 4];
		s[2*i+1] = hc[data[i] & 0xf];
	}
	return s;
}

// ---------------------------------------------------------------------------
// Emit one pair to output
// ---------------------------------------------------------------------------
static void emit(FILE *out, const uint8_t *pk, size_t pk_len)
{
	uint8_t h[20];
	hash160(pk, pk_len, h);
	std::string addr = base58check(0x00, h, 20);
	std::string pubhex = to_hex(pk, pk_len);
	fprintf(out, "%s\t%s\n", addr.c_str(), pubhex.c_str());
}

// ---------------------------------------------------------------------------
// Validate pubkey
// ---------------------------------------------------------------------------
static bool valid_pubkey(const uint8_t *p, size_t len)
{
	if (len == 33) return p[0] == 0x02 || p[0] == 0x03;
	if (len == 65) return p[0] == 0x04;
	return false;
}

// ---------------------------------------------------------------------------
// DER sig heuristic
// ---------------------------------------------------------------------------
static bool looks_like_der_sig(const uint8_t *p, size_t len)
{
	if (len < 9 || len > 73) return false;
	if (p[0] != 0x30) return false;
	if (p[1] != (uint8_t)(len - 3)) return false;
	if (p[2] != 0x02) return false;
	return true;
}

// ---------------------------------------------------------------------------
// Parse P2PKH scriptSig → emit pair
// ---------------------------------------------------------------------------
static bool parse_p2pkh_scriptsig(const uint8_t *script, size_t script_len, FILE *out)
{
	if (script_len < 10) return false;

	const uint8_t *p   = script;
	const uint8_t *end = script + script_len;

	// First push: signature
	uint8_t push1 = *p++;
	size_t  sig_len;
	if      (push1 >= 0x01 && push1 <= 0x4b) { sig_len = push1; }
	else if (push1 == 0x4c) { if (p >= end) return false; sig_len = *p++; }
	else return false;

	if ((size_t)(end - p) < sig_len) return false;
	if (!looks_like_der_sig(p, sig_len)) return false;
	p += sig_len;

	if (p >= end) return false;

	// Second push: pubkey
	uint8_t push2 = *p++;
	size_t  pk_len;
	if      (push2 >= 0x01 && push2 <= 0x4b) { pk_len = push2; }
	else if (push2 == 0x4c) { if (p >= end) return false; pk_len = *p++; }
	else return false;

	if ((size_t)(end - p) < pk_len) return false;
	const uint8_t *pk_bytes = p;

	if (!valid_pubkey(pk_bytes, pk_len)) return false;

	emit(out, pk_bytes, pk_len);
	return true;
}

// ---------------------------------------------------------------------------
// Parse one transaction from blk*.dat
// ---------------------------------------------------------------------------
static void parse_tx_blk(Reader &r, FILE *out, uint64_t &count)
{
	r.skip(4); // version

	bool segwit = false;
	if (r.remaining() >= 2 && r.p[0] == 0x00 && r.p[1] != 0x00) {
		r.skip(2);
		segwit = true;
	}

	uint64_t vin_count = r.varint();
	if (vin_count > 100000) throw std::runtime_error("implausible vin_count");

	std::vector<std::vector<uint8_t>> scripts;
	scripts.reserve((size_t)vin_count);
	for (uint64_t i = 0; i < vin_count; i++) {
		r.skip(36); // prev outpoint
		uint64_t slen = r.varint();
		if (slen > 10000) throw std::runtime_error("implausible script_len");
		scripts.push_back(r.read((size_t)slen));
		r.skip(4); // sequence
	}

	uint64_t vout_count = r.varint();
	if (vout_count > 100000) throw std::runtime_error("implausible vout_count");
	for (uint64_t i = 0; i < vout_count; i++) {
		r.skip(8);
		uint64_t slen = r.varint();
		if (slen > 10000) throw std::runtime_error("implausible script_len");
		r.skip((size_t)slen);
	}

	if (segwit) {
		for (uint64_t i = 0; i < vin_count; i++) {
			uint64_t items = r.varint();
			for (uint64_t j = 0; j < items; j++) {
				uint64_t ilen = r.varint();
				r.skip((size_t)ilen);
			}
		}
	}

	r.skip(4); // locktime

	for (const auto &sc : scripts) {
		if (sc.empty()) continue;
		if (parse_p2pkh_scriptsig(sc.data(), sc.size(), out))
			count++;
	}
}

// ---------------------------------------------------------------------------
// Scan one blk*.dat file
// ---------------------------------------------------------------------------
static void scan_blkfile(const char *path, FILE *out,
                          uint64_t &blocks, uint64_t &txs, uint64_t &pairs)
{
	FILE *f = fopen(path, "rb");
	if (!f) return;

	fseek(f, 0, SEEK_END);
	long fsize = ftell(f);
	fseek(f, 0, SEEK_SET);
	if (fsize <= 0) { fclose(f); return; }

	std::vector<uint8_t> buf((size_t)fsize);
	if (fread(buf.data(), 1, (size_t)fsize, f) != (size_t)fsize) {
		fprintf(stderr, "Read error: %s\n", path);
		fclose(f);
		return;
	}
	fclose(f);

	fprintf(stderr, "Scanning %s (%ld MB)...\n", path, fsize / 1048576);

	const uint8_t *data = buf.data();
	const uint8_t *end  = data + fsize;
	const uint8_t *p    = data;

	while (p < end) {
		if (end - p < 8) break;
		uint32_t magic = (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
		if (magic != MAINNET_MAGIC && magic != TESTNET_MAGIC && magic != SIGNET_MAGIC) {
			p++; continue;
		}
		p += 4;
		if (end - p < 4) break;
		uint32_t bsize = (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
		p += 4;
		if (bsize == 0 || bsize > 4000000) continue;
		if ((size_t)(end - p) < bsize) break;

		Reader r(p, bsize);
		p += bsize;

		try {
			r.skip(80); // block header
			uint64_t ntx = r.varint();
			if (ntx > 100000) continue;
			blocks++;
			for (uint64_t i = 0; i < ntx; i++) {
				txs++;
				parse_tx_blk(r, out, pairs);
			}
		} catch (...) {}
	}
}

// ---------------------------------------------------------------------------
// Scan all blk*.dat files
// ---------------------------------------------------------------------------
static void scan_blocks(const char *blocks_dir, FILE *out)
{
	uint64_t blocks = 0, txs = 0, pairs = 0;

	for (int n = 0; n <= 99999; n++) {
		char path[4096];
		snprintf(path, sizeof(path), "%s/blk%05d.dat", blocks_dir, n);
		FILE *test = fopen(path, "rb");
		if (!test) break;
		fclose(test);

		scan_blkfile(path, out, blocks, txs, pairs);
		fprintf(stderr, "  blk: blocks=%llu txs=%llu pairs=%llu\n",
		        (unsigned long long)blocks,
		        (unsigned long long)txs,
		        (unsigned long long)pairs);
	}

	fprintf(stderr, "blocks done. blocks=%llu txs=%llu pairs=%llu\n",
	        (unsigned long long)blocks,
	        (unsigned long long)txs,
	        (unsigned long long)pairs);
}

// ---------------------------------------------------------------------------
// Chainstate: key varint (standard Bitcoin varint used in keys, not value varint)
// ---------------------------------------------------------------------------
static uint64_t key_varint(const uint8_t *&p, const uint8_t *end)
{
	if (p >= end) throw std::runtime_error("key varint: out of data");
	uint8_t b = *p++;
	if (b < 0xfd) return b;
	if (b == 0xfd) {
		if (p + 2 > end) throw std::runtime_error("key varint: truncated");
		uint16_t v = (uint16_t)p[0] | ((uint16_t)p[1] << 8); p += 2; return v;
	}
	if (b == 0xfe) {
		if (p + 4 > end) throw std::runtime_error("key varint: truncated");
		uint32_t v = (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
		p += 4; return v;
	}
	if (p + 8 > end) throw std::runtime_error("key varint: truncated");
	uint64_t v = 0;
	for (int i = 0; i < 8; i++) v |= ((uint64_t)p[i] << (8*i));
	p += 8; return v;
}

// ---------------------------------------------------------------------------
// Scan chainstate LevelDB
// ---------------------------------------------------------------------------
static void scan_chainstate(const char *cs_dir, FILE *out)
{
	leveldb::Options opts;
	opts.create_if_missing = false;
	leveldb::DB *db = nullptr;
	leveldb::Status status = leveldb::DB::Open(opts, cs_dir, &db);
	if (!status.ok()) {
		fprintf(stderr, "chainstate LevelDB open failed: %s\n"
		        "Stop Bitcoin Core before scanning chainstate, or use a copy.\n",
		        status.ToString().c_str());
		return;
	}

	// Get obfuscation key
	std::vector<uint8_t> obf_key;
	{
		static const char obf_k[] = "\x0e\x00obfuscate_key";
		std::string val;
		if (db->Get(leveldb::ReadOptions(), leveldb::Slice(obf_k, sizeof(obf_k)-1), &val).ok()
		    && !val.empty()) {
			const uint8_t *kp = reinterpret_cast<const uint8_t *>(val.data());
			uint8_t klen = kp[0];
			obf_key.assign(kp + 1, kp + 1 + klen);
			fprintf(stderr, "chainstate obfuscation key: %s\n",
			        to_hex(obf_key.data(), obf_key.size()).c_str());
		}
	}

	leveldb::ReadOptions ropts;
	ropts.fill_cache = false;
	leveldb::Iterator *it = db->NewIterator(ropts);

	uint64_t utxos = 0, pairs = 0;

	it->Seek(leveldb::Slice("C", 1));
	for (; it->Valid(); it->Next()) {
		leveldb::Slice k = it->key();
		if (k.size() == 0 || (uint8_t)k.data()[0] != 0x43) break;

		// Deobfuscate value
		std::vector<uint8_t> val(
		    reinterpret_cast<const uint8_t *>(it->value().data()),
		    reinterpret_cast<const uint8_t *>(it->value().data()) + it->value().size()
		);
		if (!obf_key.empty()) {
			for (size_t i = 0; i < val.size(); i++)
				val[i] ^= obf_key[i % obf_key.size()];
		}

		utxos++;

		// Parse value: varint(height<<1|coinbase) + varint(amount) + varint(script_type) + data
		try {
			const uint8_t *vp  = val.data();
			const uint8_t *vend = vp + val.size();

			// Use Reader's cs-varint logic inline
			// height/coinbase
			{
				uint64_t n=0;
				while(vp<vend){uint8_t b=*vp++;n=(n<<7)|(b&0x7f);if(b&0x80)n++;else break;}
			}
			// amount
			{
				uint64_t n=0;
				while(vp<vend){uint8_t b=*vp++;n=(n<<7)|(b&0x7f);if(b&0x80)n++;else break;}
			}
			// script type
			uint64_t stype=0;
			{
				uint64_t n=0;
				while(vp<vend){uint8_t b=*vp++;n=(n<<7)|(b&0x7f);if(b&0x80)n++;else break;}
				stype=n;
			}

			// Types 2/3: compressed pubkey (prefix stored as 02/03, 32-byte X follows)
			// Types 4/5: uncompressed pubkey stored as 32-byte X only; prefix is 04
			//            but we only have X — emit as compressed (02/03 + X)
			if (stype == 2 || stype == 3) {
				if (vp + 32 > vend) continue;
				uint8_t pk[33];
				pk[0] = (stype == 2) ? 0x02 : 0x03;
				memcpy(pk + 1, vp, 32);
				emit(out, pk, 33);
				pairs++;
			} else if (stype == 4 || stype == 5) {
				// Uncompressed: only X stored; emit compressed equivalent
				// (true 65-byte uncompressed would require Y recovery via secp256k1)
				if (vp + 32 > vend) continue;
				uint8_t pk[33];
				pk[0] = (stype == 4) ? 0x02 : 0x03;
				memcpy(pk + 1, vp, 32);
				emit(out, pk, 33);
				pairs++;
			}
			// types 0,1,6+: no pubkey available
		} catch (...) {}

		if (utxos % 1000000 == 0) {
			fprintf(stderr, "  chainstate: utxos=%llu pairs=%llu\n",
			        (unsigned long long)utxos,
			        (unsigned long long)pairs);
		}
	}

	if (!it->status().ok())
		fprintf(stderr, "chainstate iterator error: %s\n", it->status().ToString().c_str());

	delete it;
	delete db;

	fprintf(stderr, "chainstate done. utxos=%llu pairs=%llu\n",
	        (unsigned long long)utxos,
	        (unsigned long long)pairs);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
int main(int argc, char *argv[])
{
	if (argc < 3) {
		fprintf(stderr,
		        "Usage:\n"
		        "  %s --blocks  <blocks_dir>      [output_file]\n"
		        "  %s --chain   <chainstate_dir>   [output_file]\n"
		        "  %s --both    <bitcoin_datadir>  [output_file]\n\n"
		        "  --blocks  : scan blk*.dat for P2PKH scriptSig pubkeys\n"
		        "  --chain   : scan chainstate UTXO set for P2PK pubkeys\n"
		        "  --both    : both sources; datadir must contain blocks/ and chainstate/\n\n"
		        "Output format (TAB separated, append mode):\n"
		        "  <address>\\t<pubkey_hex>\n",
		        argv[0], argv[0], argv[0]);
		return 1;
	}

	const char *mode     = argv[1];
	const char *datapath = argv[2];
	const char *out_path = argc >= 4 ? argv[3] : nullptr;

	FILE *out = stdout;
	if (out_path) {
		out = fopen(out_path, "a");
		if (!out) { perror("fopen output"); return 1; }
	}

	if (strcmp(mode, "--blocks") == 0) {
		scan_blocks(datapath, out);
	} else if (strcmp(mode, "--chain") == 0) {
		scan_chainstate(datapath, out);
	} else if (strcmp(mode, "--both") == 0) {
		char blocks_path[4096], chain_path[4096];
		snprintf(blocks_path, sizeof(blocks_path), "%s/blocks",     datapath);
		snprintf(chain_path,  sizeof(chain_path),  "%s/chainstate", datapath);
		scan_chainstate(chain_path, out);
		scan_blocks(blocks_path, out);
	} else {
		fprintf(stderr, "Unknown mode: %s\n", mode);
		if (out_path) fclose(out);
		return 1;
	}

	if (out_path) fclose(out);
	return 0;
}
