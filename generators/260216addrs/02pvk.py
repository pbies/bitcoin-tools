#!/usr/bin/env python3

import hashlib, random, sys
from ecdsa import SigningKey, SECP256k1

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def sha256(b):
	return hashlib.sha256(b).digest()

def ripemd160(b):
	h = hashlib.new("ripemd160")
	h.update(b)
	return h.digest()

def base58_encode(b):
	n = int.from_bytes(b, "big")
	res = ""
	while n > 0:
		n, r = divmod(n, 58)
		res = ALPHABET[r] + res

	# leading zero bytes
	pad = 0
	for byte in b:
		if byte == 0:
			pad += 1
		else:
			break

	return "1" * pad + res

def base58check(version, payload):
	data = version + payload
	checksum = sha256(sha256(data))[:4]
	return base58_encode(data + checksum)

def privkey_to_address(priv_int):
	priv_bytes = priv_int.to_bytes(32, "big")
	sk = SigningKey.from_string(priv_bytes, curve=SECP256k1)
	vk = sk.verifying_key

	# compressed public key
	x = vk.pubkey.point.x()
	y = vk.pubkey.point.y()
	prefix = b"\x02" if y % 2 == 0 else b"\x03"
	pubkey_compressed = prefix + x.to_bytes(32, "big")

	pubkey_hash = ripemd160(sha256(pubkey_compressed))
	return base58check(b"\x00", pubkey_hash)

if __name__ == "__main__":
	start = 1
	count = 255

	for i in range(start, start + count):
		j=2**i
		k=random.randint(j, j*2)
		addr = privkey_to_address(k)
		print(f"{i:>5} -> {hex(k)} -> {addr}")
	print('\a', end='', file=sys.stderr)
