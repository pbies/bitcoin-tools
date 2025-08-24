#!/usr/bin/env python3
# monero_addr_from_spend.py
# Derive a Monero mainnet standard address from a private spend key (32-byte hex).
# Requires: pynacl (for ed25519 basepoint) and pysha3 (for Keccak-256)

import argparse
import binascii
import sys

# --- Keccak-256 (Monero uses pre-NIST Keccak, provided by pysha3) ---
try:
	import sha3  # pysha3
	def keccak256(data: bytes) -> bytes:
		k = sha3.keccak_256()
		k.update(data)
		return k.digest()
except ImportError:
	sys.stderr.write("ERROR: This script needs the 'pysha3' package (pip install pysha3)\n")
	raise

# --- Ed25519 basepoint scalar multiplication (NO CLAMP) ---
try:
	from nacl.bindings import crypto_scalarmult_ed25519_base_noclamp
except Exception:
	sys.stderr.write("ERROR: This script needs PyNaCl with ed25519 noclamp bindings (pip install pynacl)\n")
	raise

# ed25519 group order L
L = 2**252 + 27742317777372353535851937790883648493

# Monero network byte prefixes (standard addresses)
PREFIX_MAINNET = 0x12  # 18 decimal
PREFIX_TESTNET = 0x35  # 53 decimal (for completeness)
PREFIX_STAGENET = 0x18 # 24 decimal (for completeness)

# --- Helpers ---
def sc_reduce32(x: bytes) -> bytes:
	"""Reduce 32-byte little-endian integer mod L, return 32-byte little-endian."""
	s = int.from_bytes(x, "little") % L
	return s.to_bytes(32, "little")

def pub_from_priv_scalar(priv_le32: bytes) -> bytes:
	"""Compute Ed25519 public key from 32-byte little-endian scalar (no clamp)."""
	if len(priv_le32) != 32:
		raise ValueError("Private scalar must be 32 bytes")
	return crypto_scalarmult_ed25519_base_noclamp(priv_le32)

# --- Monero Base58 (CryptoNote) ---
ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Map of input block sizes (in bytes) to output base58 length
B58_BLOCK_SIZES = {1:2, 2:3, 3:5, 4:6, 5:7, 6:9, 7:10, 8:11}

def _b58_encode_block_le(block: bytes, out_len: int) -> bytes:
	"""
	Encode a <=8-byte little-endian block to Monero base58 with fixed out_len.
	"""
	num = int.from_bytes(block, "little")
	enc = bytearray()
	for _ in range(out_len):
		num, rem = divmod(num, 58)
		enc.append(ALPHABET[rem])
	# If num != 0 here, something went wrong with out_len
	return bytes(enc)

def monero_base58_encode(data: bytes) -> str:
	"""
	Monero base58 encodes data in 8-byte little-endian blocks (last block shorter).
	Each full 8-byte block -> 11 chars; last partial block uses B58_BLOCK_SIZES map.
	"""
	res_parts = []
	i = 0
	while i + 8 <= len(data):
		block = data[i:i+8]
		res_parts.append(_b58_encode_block_le(block, B58_BLOCK_SIZES[8]))
		i += 8
	# remainder
	rem = data[i:]
	if rem:
		res_parts.append(_b58_encode_block_le(rem, B58_BLOCK_SIZES[len(rem)]))
	# Note: _b58_encode_block_le builds in least-significant digit first; join and reverse each block
	# to match conventional left-to-right representation.
	return b"".join(part[::-1] for part in res_parts).decode("ascii")

def derive_address_from_spend(priv_spend_hex: str, prefix: int = PREFIX_MAINNET) -> dict:
	# parse private spend key (hex -> 32 bytes LE)
	try:
		priv_spend = binascii.unhexlify(priv_spend_hex.strip())
	except binascii.Error:
		raise ValueError("Private spend key must be valid hex")
	if len(priv_spend) != 32:
		raise ValueError("Private spend key must be 32 bytes (64 hex chars)")

	# Public spend key
	pub_spend = pub_from_priv_scalar(priv_spend)

	# Private view key = keccak256(priv_spend) reduced mod L
	priv_view = sc_reduce32(keccak256(priv_spend))
	# Public view key
	pub_view = pub_from_priv_scalar(priv_view)

	# Address payload: prefix || pub_spend || pub_view
	payload = bytes([prefix]) + pub_spend + pub_view
	checksum = keccak256(payload)[:4]
	addr_bytes = payload + checksum
	address = monero_base58_encode(addr_bytes)

	return {
		"private_spend_hex": priv_spend_hex.lower(),
		"private_view_hex": priv_view[::-1].hex(),  # display as hex (little-endian); keep consistent if needed
		"public_spend_hex": pub_spend.hex(),
		"public_view_hex": pub_view.hex(),
		"address": address,
	}

def main():
	parser = argparse.ArgumentParser(description="Convert Monero private spend key to standard address (mainnet by default).")
	parser.add_argument("private_spend_key_hex", help="32-byte private spend key in hex (64 hex chars).")
	parser.add_argument("--network", choices=["mainnet","testnet","stagenet"], default="mainnet",
		help="Address network (prefix). Default: mainnet.")
	args = parser.parse_args()

	prefix = {
		"mainnet": PREFIX_MAINNET,
		"testnet": PREFIX_TESTNET,
		"stagenet": PREFIX_STAGENET,
	}[args.network]

	info = derive_address_from_spend(args.private_spend_key_hex, prefix)
	print("Monero {} standard address:".format(args.network))
	print(info["address"])
	print("\nKeys:")
	print("  Public spend:", info["public_spend_hex"])
	print("  Public view :", info["public_view_hex"])
	print("  Private view:", info["private_view_hex"])

if __name__ == "__main__":
	main()
