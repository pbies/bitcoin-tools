/*
 * Bitcoin P2PKH hash160 scanner — multithreaded C++17.
 * No OpenSSL dev headers required. SHA-256 and RIPEMD-160 embedded.
 *
 * Build:
 *   g++ -O3 -march=native -std=c++17 -pthread btc_scanner.cpp -lsecp256k1 -o btc_scanner
 *
 * Usage:
 *   ./btc_scanner [threads]
 *   Default threads = max(1, hardware_concurrency - 2)
 *   Reads hash160 (20-byte hex, one per line) from hashes.txt.
 *   Appends hits to found.txt:
 *     priv_int=<dec>|wif=<wif>|pubkey=<hex>|hash160=<hex>
 */

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <unordered_set>
#include <vector>

#include <secp256k1.h>

static constexpr uint64_t BATCH_SIZE    = 32768;
static constexpr uint64_t POLL_INTERVAL = 1000;

// ---------------------------------------------------------------------------
// SHA-256
// ---------------------------------------------------------------------------
static const uint32_t K256[64]={
	0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
	0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
	0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
	0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
	0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
	0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
	0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
	0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};
static inline uint32_t rotr32(uint32_t x,int n){return(x>>n)|(x<<(32-n));}
static void sha256_blk(uint32_t h[8],const uint8_t b[64]){
	uint32_t w[64];
	for(int i=0;i<16;++i) w[i]=((uint32_t)b[i*4]<<24)|((uint32_t)b[i*4+1]<<16)|((uint32_t)b[i*4+2]<<8)|b[i*4+3];
	for(int i=16;i<64;++i){uint32_t s0=rotr32(w[i-15],7)^rotr32(w[i-15],18)^(w[i-15]>>3),s1=rotr32(w[i-2],17)^rotr32(w[i-2],19)^(w[i-2]>>10);w[i]=w[i-16]+s0+w[i-7]+s1;}
	uint32_t a=h[0],b2=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
	for(int i=0;i<64;++i){
		uint32_t S1=rotr32(e,6)^rotr32(e,11)^rotr32(e,25),ch=(e&f)^(~e&g),t1=hh+S1+ch+K256[i]+w[i];
		uint32_t S0=rotr32(a,2)^rotr32(a,13)^rotr32(a,22),maj=(a&b2)^(a&c)^(b2&c),t2=S0+maj;
		hh=g;g=f;f=e;e=d+t1;d=c;c=b2;b2=a;a=t1+t2;
	}
	h[0]+=a;h[1]+=b2;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh;
}
static void sha256(const uint8_t* data,size_t len,uint8_t out[32]){
	uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
	uint8_t block[64]; size_t pos=0;
	while(pos+64<=len){sha256_blk(h,data+pos);pos+=64;}
	size_t rem=len-pos; std::memcpy(block,data+pos,rem); block[rem]=0x80;
	if(rem<56) std::memset(block+rem+1,0,55-rem);
	else{std::memset(block+rem+1,0,63-rem);sha256_blk(h,block);std::memset(block,0,56);}
	uint64_t bits=(uint64_t)len*8;
	for(int i=0;i<8;++i) block[56+i]=(uint8_t)(bits>>(56-8*i));
	sha256_blk(h,block);
	for(int i=0;i<8;++i){out[i*4]=(uint8_t)(h[i]>>24);out[i*4+1]=(uint8_t)(h[i]>>16);out[i*4+2]=(uint8_t)(h[i]>>8);out[i*4+3]=(uint8_t)(h[i]);}
}
static void sha256d(const uint8_t* data,size_t len,uint8_t out[32]){uint8_t t[32];sha256(data,len,t);sha256(t,32,out);}

// ---------------------------------------------------------------------------
// RIPEMD-160
// ---------------------------------------------------------------------------
static inline uint32_t rotl32(uint32_t x,int n){return(x<<n)|(x>>(32-n));}
#define FF(x,y,z) ((x)^(y)^(z))
#define GG(x,y,z) (((x)&(y))|(~(x)&(z)))
#define HH(x,y,z) (((x)|(~(y)))^(z))
#define II(x,y,z) (((x)&(z))|((y)&~(z)))
#define JJ(x,y,z) ((x)^((y)|(~(z))))
static const int RL[80]={11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6};
static const int RR[80]={8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11};
static const int XL[80]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2,4,0,5,9,7,12,2,10,14,1,3,8,11,6,15,13};
static const int XR[80]={5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14,12,15,10,4,1,5,8,7,6,2,13,14,0,3,9,11};
static const uint32_t KL[5]={0x00000000,0x5a827999,0x6ed9eba1,0x8f1bbcdc,0xa953fd4e};
static const uint32_t KR[5]={0x50a28be6,0x5c4dd124,0x6d703ef3,0x7a6d76e9,0x00000000};
static void rmd160_blk(uint32_t h[5],const uint8_t b[64]){
	uint32_t X[16];
	for(int i=0;i<16;++i) X[i]=(uint32_t)b[i*4]|((uint32_t)b[i*4+1]<<8)|((uint32_t)b[i*4+2]<<16)|((uint32_t)b[i*4+3]<<24);
	uint32_t al=h[0],bl=h[1],cl=h[2],dl=h[3],el=h[4];
	uint32_t ar=h[0],br=h[1],cr=h[2],dr=h[3],er=h[4];
	for(int i=0;i<80;++i){
		uint32_t fl,fr;
		if(i<16){fl=FF(bl,cl,dl);fr=JJ(br,cr,dr);}
		else if(i<32){fl=GG(bl,cl,dl);fr=II(br,cr,dr);}
		else if(i<48){fl=HH(bl,cl,dl);fr=HH(br,cr,dr);}
		else if(i<64){fl=II(bl,cl,dl);fr=GG(br,cr,dr);}
		else{fl=JJ(bl,cl,dl);fr=FF(br,cr,dr);}
		uint32_t tmp=rotl32(al+fl+X[XL[i]]+KL[i/16],RL[i])+el;
		al=el;el=dl;dl=rotl32(cl,10);cl=bl;bl=tmp;
		tmp=rotl32(ar+fr+X[XR[i]]+KR[i/16],RR[i])+er;
		ar=er;er=dr;dr=rotl32(cr,10);cr=br;br=tmp;
	}
	uint32_t t=h[1]+cl+dr;
	h[1]=h[2]+dl+er;h[2]=h[3]+el+ar;h[3]=h[4]+al+br;h[4]=h[0]+bl+cr;h[0]=t;
}
static void ripemd160(const uint8_t* data,size_t len,uint8_t out[20]){
	uint32_t h[5]={0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0};
	uint8_t block[64]; size_t pos=0;
	while(pos+64<=len){rmd160_blk(h,data+pos);pos+=64;}
	size_t rem=len-pos; std::memcpy(block,data+pos,rem); block[rem]=0x80;
	if(rem<56) std::memset(block+rem+1,0,55-rem);
	else{std::memset(block+rem+1,0,63-rem);rmd160_blk(h,block);std::memset(block,0,56);}
	uint64_t bits=(uint64_t)len*8;
	for(int i=0;i<8;++i) block[56+i]=(uint8_t)(bits>>(8*i));
	rmd160_blk(h,block);
	for(int i=0;i<5;++i){out[i*4]=(uint8_t)(h[i]);out[i*4+1]=(uint8_t)(h[i]>>8);out[i*4+2]=(uint8_t)(h[i]>>16);out[i*4+3]=(uint8_t)(h[i]>>24);}
}
static void hash160(const uint8_t* in,size_t len,uint8_t out[20]){uint8_t sha[32];sha256(in,len,sha);ripemd160(sha,32,out);}

// ---------------------------------------------------------------------------
// U256 — private key as 4 x uint64 big-endian limbs
// ---------------------------------------------------------------------------
struct U256{
	uint64_t d[4];
	bool is_zero()const{return!d[0]&&!d[1]&&!d[2]&&!d[3];}
	void to_bytes(uint8_t b[32])const{for(int i=0;i<4;++i){uint64_t v=d[i];for(int j=7;j>=0;--j){b[i*8+j]=(uint8_t)(v&0xFF);v>>=8;}}}
	U256 add_u64(uint64_t v)const{
		U256 r=*this;
		for(int i=3;i>=0&&v;--i){unsigned __int128 s=(unsigned __int128)r.d[i]+v;r.d[i]=(uint64_t)s;v=(uint64_t)(s>>64);}
		return r;
	}
	std::string to_decimal()const{
		uint32_t mag[8];
		for(int i=0;i<4;++i){mag[i*2]=(uint32_t)(d[i]>>32);mag[i*2+1]=(uint32_t)(d[i]&0xFFFFFFFF);}
		std::string r; r.reserve(80);
		for(;;){bool z=true;for(auto x:mag)if(x){z=false;break;}if(z)break;uint64_t rem=0;for(auto&x:mag){uint64_t c=(rem<<32)|x;x=(uint32_t)(c/10);rem=c%10;}r+=(char)('0'+rem);}
		if(r.empty())r="0"; std::reverse(r.begin(),r.end()); return r;
	}
};

// ---------------------------------------------------------------------------
// WIF encoder
// ---------------------------------------------------------------------------
static const char B58A[]="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
static std::string b58enc(const uint8_t* data,size_t len){
	int lead=0; for(size_t i=0;i<len&&data[i]==0;++i)++lead;
	std::vector<uint8_t> dg; dg.reserve(len*2);
	for(size_t i=0;i<len;++i){int c=data[i];for(auto&d:dg){c+=(int)d*256;d=c%58;c/=58;}while(c){dg.push_back(c%58);c/=58;}}
	std::string out(lead,'1'); for(auto it=dg.rbegin();it!=dg.rend();++it)out+=B58A[*it]; return out;
}
static std::string wif(const uint8_t priv[32]){
	uint8_t p[38]; p[0]=0x80; std::memcpy(p+1,priv,32); p[33]=0x01;
	uint8_t ck[32]; sha256d(p,34,ck); std::memcpy(p+34,ck,4);
	return b58enc(p,38);
}

// ---------------------------------------------------------------------------
// Hex hash160 parser
// ---------------------------------------------------------------------------
static bool hex_to_h160(const std::string& hex,uint8_t h160[20]){
	if(hex.size()!=40) return false;
	for(int i=0;i<20;++i){
		auto hc=[](char c)->int{
			if(c>='0'&&c<='9')return c-'0';
			if(c>='a'&&c<='f')return c-'a'+10;
			if(c>='A'&&c<='F')return c-'A'+10;
			return -1;
		};
		int hi=hc(hex[i*2]),lo=hc(hex[i*2+1]);
		if(hi<0||lo<0)return false;
		h160[i]=(uint8_t)((hi<<4)|lo);
	}
	return true;
}

// ---------------------------------------------------------------------------
// Hash160 set
// ---------------------------------------------------------------------------
struct H160Hash{
	size_t operator()(const std::array<uint8_t,20>&a)const{
		size_t h=0;
		for(int i=0;i<20;i+=8){uint64_t v=0;for(int j=0;j<8&&i+j<20;++j)v=(v<<8)|a[i+j];h^=std::hash<uint64_t>{}(v)+0x9e3779b9+(h<<6)+(h>>2);}
		return h;
	}
};
using H160Set=std::unordered_set<std::array<uint8_t,20>,H160Hash>;

// ---------------------------------------------------------------------------
// Globals
// ---------------------------------------------------------------------------
static std::atomic<bool>     g_found{false};
static std::atomic<uint64_t> g_total{0};
static std::mutex            g_out_mutex;
static std::ofstream         g_found_file;

// ---------------------------------------------------------------------------
// Worker
// ---------------------------------------------------------------------------
static void worker(const H160Set* targets,secp256k1_context* ctx){
	std::mt19937_64 rng{std::random_device{}()};
	uint8_t priv_bytes[32],pub_ser[33],h160_buf[20];
	size_t pub_len=33;

	while(!g_found.load(std::memory_order_relaxed)){
		U256 base;
		base.d[0]=rng()&0xFFFFFFFFFFFFFFFDULL;
		base.d[1]=rng(); base.d[2]=rng(); base.d[3]=rng();
		if(base.is_zero()) continue;

		uint64_t local=0;

		for(uint64_t i=0;i<BATCH_SIZE;++i){
			if((i&(POLL_INTERVAL-1))==0&&g_found.load(std::memory_order_relaxed))
				goto done;

			U256 x=base.add_u64(i);
			x.to_bytes(priv_bytes);

			secp256k1_pubkey pubkey;
			if(!secp256k1_ec_pubkey_create(ctx,&pubkey,priv_bytes)) continue;
			pub_len=33;
			secp256k1_ec_pubkey_serialize(ctx,pub_ser,&pub_len,&pubkey,SECP256K1_EC_COMPRESSED);

			hash160(pub_ser,33,h160_buf);
			++local;

			std::array<uint8_t,20> key;
			std::memcpy(key.data(),h160_buf,20);

			if(targets->count(key)){
				g_found.store(true,std::memory_order_relaxed);
				std::ostringstream h160_hex,pk_hex;
				h160_hex<<std::hex<<std::setfill('0');
				for(int b=0;b<20;++b) h160_hex<<std::setw(2)<<(int)h160_buf[b];
				pk_hex<<std::hex<<std::setfill('0');
				for(int b=0;b<33;++b) pk_hex<<std::setw(2)<<(int)pub_ser[b];
				std::string w=wif(priv_bytes);
				std::string priv_dec=x.to_decimal();
				std::cout<<"\n\aFound! hash160: "<<h160_hex.str()<<std::endl;
				std::lock_guard<std::mutex> lk(g_out_mutex);
				g_found_file<<"priv_int="<<priv_dec<<"|wif="<<w<<"|pubkey="<<pk_hex.str()<<"|hash160="<<h160_hex.str()<<"\n";
				g_found_file.flush();
				goto done;
			}
		}
		done:
		g_total.fetch_add(local,std::memory_order_relaxed);
	}
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------
int main(int argc,char* argv[]){
	int nthreads=std::max(1,(int)std::thread::hardware_concurrency()-2);
	if(argc>1) nthreads=std::max(1,std::atoi(argv[1]));

	std::cout<<"Loading targets..."<<std::endl;
	std::ifstream af("hashes.txt");
	if(!af){std::cerr<<"Error: hashes.txt not found!\n";return 1;}

	H160Set targets;
	std::string line; int skipped=0;
	while(std::getline(af,line)){
		while(!line.empty()&&(line.back()=='\r'||line.back()=='\n'||line.back()==' '))line.pop_back();
		if(line.empty()||line[0]=='#') continue;
		std::array<uint8_t,20> h;
		if(hex_to_h160(line,h.data())) targets.insert(h);
		else{std::cerr<<"Warning: skipping: "<<line<<"\n";++skipped;}
	}
	if(targets.empty()){std::cerr<<"No valid targets!\n";return 1;}

	std::cout<<"Loaded "<<targets.size()<<" targets";
	if(skipped) std::cout<<" | skipped "<<skipped;
	std::cout<<"\n";

	g_found_file.open("found.txt",std::ios::app);
	if(!g_found_file){std::cerr<<"Error: cannot open found.txt\n";return 1;}

	secp256k1_context* ctx=secp256k1_context_create(SECP256K1_CONTEXT_SIGN);

	auto start=std::chrono::steady_clock::now();
	auto sys_t=std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
	std::string start_str=std::ctime(&sys_t);
	while(!start_str.empty()&&(start_str.back()=='\n'||start_str.back()=='\r'))start_str.pop_back();

	std::cout<<"Program started: "<<start_str<<"\n";
	std::cout<<"Threads: "<<nthreads<<" | BATCH_SIZE: "<<BATCH_SIZE<<"\n";
	std::cout<<"Searching...\n";

	std::vector<std::thread> workers;
	workers.reserve(nthreads);
	for(int i=0;i<nthreads;++i) workers.emplace_back(worker,&targets,ctx);

	std::thread reporter([&]{
		uint64_t last=0; auto lt=std::chrono::steady_clock::now();
		while(!g_found.load(std::memory_order_relaxed)){
			std::this_thread::sleep_for(std::chrono::seconds(2));
			if(g_found.load(std::memory_order_relaxed)) break;
			auto now=std::chrono::steady_clock::now();
			uint64_t tot=g_total.load(std::memory_order_relaxed);
			double ela=std::chrono::duration<double>(now-start).count();
			double per=std::chrono::duration<double>(now-lt).count();
			uint64_t dlt=tot-last;
			double cur=(per>0)?(double)dlt/per:0.0;
			double avg=(ela>0)?(double)tot/ela:0.0;
			std::cout<<"Total: "<<tot<<" | Speed: "<<std::fixed<<std::setprecision(0)
			         <<cur<<"/s (cur) | "<<avg<<"/s (avg)"
			         <<" | Running: "<<std::setprecision(1)<<ela<<"s   \r"<<std::flush;
			last=tot; lt=now;
		}
	});

	for(auto& t:workers) t.join();
	reporter.join();

	secp256k1_context_destroy(ctx);

	auto end=std::chrono::steady_clock::now();
	double tsec=std::chrono::duration<double>(end-start).count();
	uint64_t tkeys=g_total.load();

	std::cout<<"\n\nFinal: "<<tkeys<<" keys in "<<std::fixed<<std::setprecision(1)<<tsec<<"s ("
	         <<std::setprecision(0)<<(tsec>0?tkeys/tsec:0)<<" keys/sec)\n";

	auto stop_t=std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
	std::string stop_str=std::ctime(&stop_t);
	while(!stop_str.empty()&&(stop_str.back()=='\n'||stop_str.back()=='\r'))stop_str.pop_back();
	uint64_t s=(uint64_t)tsec;
	std::cout<<"Program started:  "<<start_str<<"\n";
	std::cout<<"Program stopped:  "<<stop_str<<"\n";
	std::cout<<"Execution took:   "<<s/3600<<"h "<<(s%3600)/60<<"m "<<s%60<<"s\n";
	return 0;
}
