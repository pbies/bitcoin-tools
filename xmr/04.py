#!/usr/bin/env python3
# monero_addr_from_spend_fixed.py
# Piotr-friendly: opcjonalna konwersja big->little endian, redukcja mod L, walidacja adresu

from tqdm import tqdm
import argparse, binascii, sys
try:
	import sha3  # pysha3: Keccak-256 (pre-NIST)
except ImportError:
	sys.stderr.write("ERROR: pip install pysha3\n"); raise

try:
	from nacl.bindings import crypto_scalarmult_ed25519_base_noclamp
except Exception:
	sys.stderr.write("ERROR: pip install pynacl\n"); raise

L = 2**252 + 27742317777372353535851937790883648493
PREFIX_MAINNET = 0x12
ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
B58_BLOCK_SIZES = {1:2,2:3,3:5,4:6,5:7,6:9,7:10,8:11}

def keccak256(b: bytes) -> bytes:
	k = sha3.keccak_256(); k.update(b); return k.digest()

def sc_reduce32(x: bytes) -> bytes:
	return (int.from_bytes(x, "little") % L).to_bytes(32, "little")

def pub_from_scalar_le(x_le32: bytes) -> bytes:
	if len(x_le32) != 32: raise ValueError("scalar must be 32 bytes")
	return crypto_scalarmult_ed25519_base_noclamp(x_le32)

def _b58_block_le(block: bytes, out_len: int) -> bytes:
	# CryptoNote: 8-bajtowe bloki interpretowane jako LE; 11 cyfr dla 8B itd.
	num = int.from_bytes(block, "little")
	out = bytearray()
	for _ in range(out_len):
		num, rem = divmod(num, 58)
		out.append(ALPHABET[rem])
	return bytes(out[::-1])

def monero_base58_encode(data: bytes) -> str:
	out = []
	i = 0
	while i + 8 <= len(data):
		out.append(_b58_block_le(data[i:i+8], B58_BLOCK_SIZES[8]))
		i += 8
	if i < len(data):
		last = data[i:]
		out.append(_b58_block_le(last, B58_BLOCK_SIZES[len(last)]))
	return b"".join(out).decode("ascii")

def monero_base58_decode(addr: str) -> bytes:
	# Tylko do walidacji (prosta wersja)
	def dec_block(s: str) -> bytes:
		num = 0
		for ch in s:
			num = num*58 + ALPHABET.index(ch.encode()[0])
		# dobierz długość na bazie długości bloku b58
		l = {11:8,10:7,9:6,7:5,6:4,5:3,3:2,2:1}[len(s)]
		return num.to_bytes(l, "little")
	# 95 znaków => 8*11 + 7 = 95
	data = b"".join([
		dec_block(addr[i:i+11]) for i in range(0, 88, 11)
	] + [dec_block(addr[88:])])
	return data

def derive_address(priv_spend_hex: str, input_endian: str = "little", prefix: int = PREFIX_MAINNET):
	raw = binascii.unhexlify(priv_spend_hex.strip())
	if len(raw) != 32:
		raise ValueError("private spend key must be 32 bytes (64 hex)")

	# zaakceptuj big-endian na wejściu, przelicz do LE (Monero używa LE)
	priv_spend_le = raw if input_endian == "little" else raw[::-1]
	priv_spend_le = sc_reduce32(priv_spend_le)

	pub_spend = pub_from_scalar_le(priv_spend_le)
	priv_view_le = sc_reduce32(keccak256(priv_spend_le))
	pub_view  = pub_from_scalar_le(priv_view_le)

	payload = bytes([prefix]) + pub_spend + pub_view
	checksum = keccak256(payload)[:4]
	addr = monero_base58_encode(payload + checksum)

	return {
		"private_spend_hex": priv_spend_le.hex(),   # LE – tak drukuje Monero
		"private_view_hex":  priv_view_le.hex(),
		"public_spend_hex":  pub_spend.hex(),
		"public_view_hex":   pub_view.hex(),
		"address":           addr,
	}

def is_valid_mainnet_address(addr: str) -> bool:
	try:
		raw = monero_base58_decode(addr)
	except Exception:
		return False
	if len(raw) != 1+32+32+4: return False
	if raw[0] != PREFIX_MAINNET: return False
	return keccak256(raw[:-4])[:4] == raw[-4:]

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--input-endian", choices=["little","big"], default="little",
		help="Endian wejściowego hex klucza (domyślnie little – jak w Monero).")
	ap.add_argument("--prefix", type=lambda x:int(x,0), default=PREFIX_MAINNET,
		help="Prefiks sieci (0x12 mainnet).")
	ap.add_argument("-i","--input", default="input.txt")
	ap.add_argument("-o","--output", default="output.txt")
	args = ap.parse_args()

	open(args.output, "w").close()
	for line in tqdm(open(args.input, "r").read().splitlines()):
		h = line.strip()
		if not h: continue
		try:
			info = derive_address(h, args.input_endian, args.prefix)
			ok = is_valid_mainnet_address(info["address"])
		except Exception as e:
			sys.stderr.write(f"[SKIP] {h[:16]}… : {e}\n"); continue
		with open(args.output, "a") as o:
			o.write(f"Address: {info['address']}{'  [OK]\n' if ok else '  [BAD]\n'}")
			o.write(f"  Public spend: {info['public_spend_hex']}\n")
			o.write(f"  Private spend: {info['private_spend_hex']}\n")
			o.write(f"  Public view : {info['public_view_hex']}\n")
			o.write(f"  Private view: {info['private_view_hex']}\n\n")

if __name__ == "__main__":
	main()
