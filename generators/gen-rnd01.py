#!/usr/bin/env python3

import os
import time
import hmac
import hashlib
import secrets
import random
import struct
from typing import Callable

# secp256k1 curve order (Bitcoin private keys must be in [1, n-1])
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def _int_to_hex_32(i: int) -> str:
	return f"{i:064x}"

def _bytes_to_int(b: bytes) -> int:
	return int.from_bytes(b, "big")

def _sample_privkey_from_int_source(get_int_256: Callable[[], int]) -> int:
	# Rejection sampling for uniform distribution in [1, n-1]
	while True:
		k = get_int_256()
		if 1 <= k < SECP256K1_N:
			return k

def _sample_privkey_from_bytes_source(get_bytes_32: Callable[[], bytes]) -> int:
	while True:
		k = _bytes_to_int(get_bytes_32())
		if 1 <= k < SECP256K1_N:
			return k

# 1) secrets.randbits (CSPRNG)
def gen1() -> int:
	return _sample_privkey_from_int_source(lambda: secrets.randbits(256))

# 2) secrets.token_bytes (CSPRNG)
def gen2() -> int:
	return _sample_privkey_from_bytes_source(lambda: secrets.token_bytes(32))

# 3) os.urandom (CSPRNG)
def gen3() -> int:
	return _sample_privkey_from_bytes_source(lambda: os.urandom(32))

# 4) random.SystemRandom().getrandbits (CSPRNG)
_SYSR = random.SystemRandom()
def gen4() -> int:
	return _sample_privkey_from_int_source(lambda: _SYSR.getrandbits(256))

# 5) SHA256(os.urandom(64)) -> 32 bytes (CSPRNG-seeded hash)
def gen5() -> int:
	def _b() -> bytes:
		return hashlib.sha256(os.urandom(64)).digest()
	return _sample_privkey_from_bytes_source(_b)

# 6) SHA512(os.urandom(64)) then take first 32 bytes (CSPRNG-seeded hash)
def gen6() -> int:
	def _b() -> bytes:
		return hashlib.sha512(os.urandom(64)).digest()[:32]
	return _sample_privkey_from_bytes_source(_b)

# 7) BLAKE2b(os.urandom(64), digest_size=32) (CSPRNG-seeded hash)
def gen7() -> int:
	def _b() -> bytes:
		return hashlib.blake2b(os.urandom(64), digest_size=32).digest()
	return _sample_privkey_from_bytes_source(_b)

# 8) HMAC-SHA256(key=os.urandom(32), msg=counter||os.urandom(16)) (CSPRNG-seeded MAC)
_HMAC_KEY_8 = os.urandom(32)
_HMAC_CTR_8 = 0
def gen8() -> int:
	global _HMAC_CTR_8
	_HMAC_CTR_8 += 1
	msg = struct.pack(">Q", _HMAC_CTR_8) + os.urandom(16)
	def _b() -> bytes:
		return hmac.new(_HMAC_KEY_8, msg, hashlib.sha256).digest()
	return _sample_privkey_from_bytes_source(_b)

# 9) HKDF-like expand with HMAC-SHA256 (CSPRNG-seeded)
_HKDF_SALT_9 = os.urandom(32)
_HKDF_IKM_9 = os.urandom(64)
_HKDF_PRK_9 = hmac.new(_HKDF_SALT_9, _HKDF_IKM_9, hashlib.sha256).digest()
_HKDF_CTR_9 = 0
def gen9() -> int:
	global _HKDF_CTR_9
	_HKDF_CTR_9 += 1
	info = b"privkey-gen-9"
	t = hmac.new(_HKDF_PRK_9, info + bytes([_HKDF_CTR_9 & 0xFF]), hashlib.sha256).digest()
	return _sample_privkey_from_bytes_source(lambda: t)

# 10) Deterministic stream from SHA256(seed||counter) (seeded once from CSPRNG)
_STREAM_SEED_10 = os.urandom(32)
_STREAM_CTR_10 = 0
def gen10() -> int:
	global _STREAM_CTR_10
	_STREAM_CTR_10 += 1
	b = hashlib.sha256(_STREAM_SEED_10 + struct.pack(">Q", _STREAM_CTR_10)).digest()
	return _sample_privkey_from_bytes_source(lambda: b)

METHODS = [
	("01_secrets_randbits", gen1),
	("02_secrets_token_bytes", gen2),
	("03_os_urandom", gen3),
	("04_systemrandom_getrandbits", gen4),
	("05_sha256_urandom64", gen5),
	("06_sha512_urandom64_first32", gen6),
	("07_blake2b_urandom64_32", gen7),
	("08_hmac_sha256_counter", gen8),
	("09_hkdf_like_hmac_expand", gen9),
	("10_sha256_seeded_counter", gen10),
]

def main() -> None:
	for name, fn in METHODS:
		print(f"# {name}")
		for _ in range(256):
			print(_int_to_hex_32(fn()))
		print()

if __name__ == "__main__":
	main()
