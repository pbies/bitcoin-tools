#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Uwaga: taby zamiast spacji wcięć.

import base58
import hashlib
import os
import random
import secrets
import datetime
import math
import re
import ecdsa


# === Konwersje / utils ===

def hex_to_b58c(h: str) -> str:
	"""HEX → Base58Check (bezpośrednie zakodowanie payloadu)."""
	return base58.b58encode_check(bytes.fromhex(h)).decode("ascii")


def int_to_b58c_wif(n: int, *, compressed: bool = True) -> str:
	"""Int → 32B priv → WIF (mainnet)."""
	if not (1 <= n < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141):
		raise ValueError("wartość poza zakresem secp256k1")
	key = n.to_bytes(32, "big")
	return pvk_to_wif(key, compressed=compressed)


def int_to_bytes3(value: int, length: int | None = None) -> bytes:
	"""Int → bytes (big endian). Dla 0 zwraca b'\\x00' gdy length nie podano."""
	if value == 0 and not length:
		return b"\x00"
	if not length:
		length = (value.bit_length() + 7) // 8 or 1
	return value.to_bytes(length, "big")


def int_to_bytes4(number: int, length: int) -> bytes:
	"""Alias do number.to_bytes(length, 'big') — dla kompatybilności nazw."""
	return number.to_bytes(length, "big")


def bytes_to_int(k: bytes) -> int:
	return int.from_bytes(k, "big")


def find_all_matches(pattern: str, string: str) -> list[str]:
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out


# === Hashowanie ===

def sha256(data: bytes) -> bytes:
	return hashlib.sha256(data).digest()


def ripemd160(data: bytes) -> bytes:
	h = hashlib.new("ripemd160")
	h.update(data)
	return h.digest()


def hash160(data: bytes) -> bytes:
	return ripemd160(sha256(data))


# === Klucze / adresy (Bitcoin mainnet, P2PKH) ===

def pvk_to_wif(key_bytes: bytes, *, compressed: bool = True) -> str:
	"""
	32B private key → WIF (mainnet).
	Jeśli compressed=True, dokleja 0x01 przed checksumą (klucz dla pubkey compressed).
	"""
	if len(key_bytes) != 32:
		raise ValueError("klucz prywatny musi mieć 32 bajty")
	payload = b"\x80" + key_bytes + (b"\x01" if compressed else b"")
	return base58.b58encode_check(payload).decode("ascii")


def pvk_to_wif2(key_hex: str, *, compressed: bool = True) -> str:
	return pvk_to_wif(bytes.fromhex(key_hex), compressed=compressed)


def wif_to_private_key(wif: str) -> bytes:
	"""
	WIF → surowy 32B klucz.
	Obsługa obu wariantów (z i bez 0x01). Zwraca wyłącznie 32 bajty.
	"""
	decoded = base58.b58decode_check(wif)
	if len(decoded) == 34 and decoded[0] == 0x80 and decoded[-1] == 0x01:
		return decoded[1:-1]
	if len(decoded) == 33 and decoded[0] == 0x80:
		return decoded[1:]
	raise ValueError("niepoprawny WIF")


def pvk_to_pubkey(priv_hex: str) -> str:
	"""HEX 32B priv → uncompressed public key (0x04 || X || Y) jako HEX."""
	sk = ecdsa.SigningKey.from_string(bytes.fromhex(priv_hex), curve=ecdsa.SECP256k1)
	return (b"\x04" + sk.verifying_key.to_string()).hex()


def privkey_to_pubkey(privkey: bytes, *, compressed: bool = True) -> bytes:
	"""Zwraca pubkey (33B skompresowany lub 65B nieskompresowany)."""
	if len(privkey) != 32:
		raise ValueError("privkey musi mieć 32 bajty")
	sk = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	if compressed:
		prefix = b"\x03" if (vk.pubkey.point.y() & 1) else b"\x02"
		return prefix + int_to_bytes3(vk.pubkey.point.x(), 32)
	return b"\x04" + int_to_bytes3(vk.pubkey.point.x(), 32) + int_to_bytes3(vk.pubkey.point.y(), 32)


# — Kompresja / dekompresja pubkey —

_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F  # secp256k1 prime


def decompress_pubkey(pk: bytes) -> bytes:
	"""
	Wejście: 33B skompresowany (02/03 || X).
	Wyjście: 65B nieskompresowany (04 || X || Y).
	"""
	if not (isinstance(pk, (bytes, bytearray)) and len(pk) == 33 and pk[0] in (2, 3)):
		raise ValueError("Oczekiwano skompresowanego klucza publicznego (33 bajty)")
	x = int.from_bytes(pk[1:], "big")
	alpha = (pow(x, 3, _P) + 7) % _P
	y = pow(alpha, (_P + 1) // 4, _P)  # sqrt mod p
	if (y & 1) != (pk[0] & 1):
		y = (-y) % _P
	return b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")


def compress_pubkey_from_uncompressed_hex(uncompressed_hex: str) -> str:
	"""
	Wejście: HEX nieskompresowany (04 || X || Y).
	Wyjście: HEX skompresowany (02/03 || X).
	"""
	raw = bytes.fromhex(uncompressed_hex)
	if not (len(raw) == 65 and raw[0] == 0x04):
		raise ValueError("Oczekiwano nieskompresowanego klucza (65 bajtów, prefix 0x04)")
	x = int.from_bytes(raw[1:33], "big")
	y = int.from_bytes(raw[33:], "big")
	prefix = 0x02 if (y % 2 == 0) else 0x03
	return bytes([prefix]) + x.to_bytes(32, "big")
	

def pubkey_to_p2pkh_address(pubkey_bytes: bytes) -> str:
	"""Dowolny pubkey (compressed lub uncompressed) → adres P2PKH (mainnet)."""
	h160 = hash160(pubkey_bytes)
	return base58.b58encode_check(b"\x00" + h160).decode("ascii")


def private_key_to_address(private_key_bytes: bytes, *, compressed: bool = True) -> str:
	"""P2PKH z privkey (z wyborem formatu pubkey)."""
	pub = privkey_to_pubkey(private_key_bytes, compressed=compressed)
	return pubkey_to_p2pkh_address(pub)


# === RNG / narzędzia różne ===

def generate_random_private_key() -> str:
	"""Silny RNG (secrets)."""
	return secrets.token_hex(32)


def generate_random_private_key1() -> str:
	"""random.getrandbits — nie kryptograficzny (zostawione dla zgodności nazw)."""
	return hex(random.getrandbits(256))[2:].zfill(64)


def generate_random_private_key2() -> str:
	"""os.urandom — kryptograficzny."""
	return os.urandom(32).hex()


def generate_random_private_key3() -> str:
	"""Los w zakresie [1..N-1] — niekryptograficzny (random)."""
	return hex(random.randint(1, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140))[2:].zfill(64)


def generate_random_private_key4() -> str:
	"""alias do secrets.token_hex(32)."""
	return secrets.token_hex(32)


# === Opcjonalne: BST (bez efektów ubocznych) ===

class Node:
	def __init__(self, data):
		self.left = None
		self.right = None
		self.data = data

	def insert(self, data):
		if data < self.data:
			if self.left is None:
				self.left = Node(data)
			else:
				self.left.insert(data)
		elif data > self.data:
			if self.right is None:
				self.right = Node(data)
			else:
				self.right.insert(data)

def buildTree(sorted_values: list, start: int, end: int):
	if start > end:
		return None
	mid = start + (end - start) // 2
	node = Node(sorted_values[mid])
	node.left = buildTree(sorted_values, start, mid - 1)
	node.right = buildTree(sorted_values, mid + 1, end)
	return node

def search(root: Node | None, key):
	if root is None or root.data == key:
		return root
	if key > root.data:
		return search(root.right, key)
	return search(root.left, key)


# === Tryb demo / sanity-check (nic nie zapisuje do plików automatycznie) ===

if __name__ == "__main__":
	# Prosty self-test na przykładowym kluczu:
	priv = bytes.fromhex("11" * 32)

	wif_c = pvk_to_wif(priv, compressed=True)
	wif_u = pvk_to_wif(priv, compressed=False)
	print("WIF (compressed):", wif_c)
	print("WIF (uncompressed):", wif_u)
	assert wif_to_private_key(wif_c) == priv
	assert wif_to_private_key(wif_u) == priv

	pub_c = privkey_to_pubkey(priv, compressed=True)
	pub_u = privkey_to_pubkey(priv, compressed=False)
	print("addr (P2PKH, compressed):", pubkey_to_p2pkh_address(pub_c))
	print("addr (P2PKH, uncompressed):", pubkey_to_p2pkh_address(pub_u))

	unc_from_c = decompress_pubkey(pub_c)
	assert unc_from_c == pub_u

	print("sanity: OK")
