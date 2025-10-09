#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from bech32 import bech32_encode, convertbits
from ecdsa import SigningKey, SECP256k1
from typing import Iterable, List
import base58
import binascii
import datetime
import ecdsa
import hashlib
import math
import os
import random
import re
import secrets

DEFAULT_BECH32_HRP = "cro"
path = "m/44'/0'/0'/0/0"

# --- Stałe secp256k1 ---
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
GPOINT = (Gx, Gy)

# --- Base58 helpers ---
def b58c_to_bytes(s: str) -> bytes:
	return base58.b58decode_check(s)

def bytes_to_b58c(b: bytes) -> str:
	return base58.b58encode_check(b).decode()

def b58c_to_hex(s: str) -> str:
	return base58.b58decode_check(s).hex()

def hex_to_b58c(h: str) -> str:
	return base58.b58encode_check(bytes.fromhex(h)).decode()


# --- Conversion helpers ---
def bytes_to_string(b: bytes) -> str:
	return b.decode("utf-8")

def bytes_to_int(b: bytes) -> int:
	return int.from_bytes(b, "big")

def bytes_to_hex(b: bytes) -> str:
	return b.hex()

def hex_to_bytes(h: str) -> bytes:
	return bytes.fromhex(h)

def hex_to_int(h: str) -> int:
	return int(h, 16)

def hex_to_string(h: str) -> str:
	return bytes.fromhex(h).decode("utf-8")

def int_to_bytes(value: int, length: int | None = None) -> bytes:
	if value == 0 and not length:
		return b"\x00"
	return value.to_bytes(length or (value.bit_length() + 7) // 8, "big")

def int_to_hex(i: int) -> str:
	return format(i, "x")  # czysty hex, bez "0x"

def int_to_str(i: int) -> str:
	return str(i)

def str_to_bytes(s: str) -> bytes:
	return s.encode()

def str_to_hex(s: str) -> str:
	return s.encode().hex()

def reverse_string(s: str) -> str:
	return s[::-1]


# --- Hashing ---
def sha256(b: bytes) -> bytes:
	return hashlib.sha256(b).digest()

def sha256_hex(b: bytes) -> str:
	return hashlib.sha256(b).hexdigest()

def ripemd160(b: bytes) -> bytes:
	return hashlib.new("ripemd160", b).digest()

def ripemd160_hex(b: bytes) -> str:
	return hashlib.new("ripemd160", b).hexdigest()

def hash160(data: bytes) -> bytes:
	return ripemd160(sha256(data))


# --- Bitcoin keys/addresses ---
def pubkey_to_addr(pubkey_hex: str) -> str:
	pubkey_bytes = bytes.fromhex(pubkey_hex)
	vh160 = b"\x00" + hash160(pubkey_bytes)
	checksum = sha256(sha256(vh160))[:4]
	return base58.b58encode(vh160 + checksum).decode()

def pvk_to_pubkey(key: bytes | str) -> str:
	key_bytes = bytes.fromhex(key) if isinstance(key, str) else key
	sk = SigningKey.from_string(key_bytes, curve=SECP256k1)
	return (b"\x04" + sk.verifying_key.to_string()).hex()

def pvk_to_addr(pvk: bytes | str) -> str:
	return pubkey_to_addr(pvk_to_pubkey(pvk))

def pvk_to_wif(key_bytes: bytes) -> str:
	return base58.b58encode_check(b"\x80" + key_bytes).decode()

def wif_to_pvk(wif: str) -> str:
	return base58.b58decode_check(wif)[1:].hex()

def entropy_to_pvk(e: str) -> str | None:
	order = SECP256k1.order
	entropy_int = int(e, 16)
	if not (1 <= entropy_int < order):
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	return private_key.to_string().hex()

def generate_random_private_key() -> str:
	return secrets.token_hex(32)


# --- Utils ---
def count_lines(file: str) -> int:
	with open(file, "r") as f:
		return sum(1 for _ in f)

def substring_after(s, delim):
	return s.partition(delim)[2]

def substring_before(s, delim):
	return s.partition(delim)[0]

def find_all_matches(pattern, string):
	import re
	pat = re.compile(pattern)
	return [m.group(0) for m in pat.finditer(string)]

def log(message: str):
	ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open("log.txt", "a") as f:
		f.write(f"{ts} {message}\n")
	print(f"{ts} {message}", flush=True)


# --- Test run ---
if __name__ == "__main__":
	print(b58c_to_bytes('1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY'))
	print(bytes_to_b58c(b'\x00\xc8%\xa1\xec\xf2\xa6\x83\x0cD\x01b\x0c:\x16\xf1\x99PW\xc2\xab'))
	print(bytes_to_string(b'abc123'))
	print(bytes_to_int(b'\x80\x00'))
	print(bytes_to_hex(b'\x80\x00'))
	print(count_lines(__file__))
	print(hex_to_bytes('8000'))
	print(hex_to_int('8000'))
	print(int_to_bytes(32768))
	print(int_to_str(65))
	print(int_to_hex(32768))
	print(pubkey_to_addr('0430210c23b1a047bc9bdbb13448e67deddc108946de6de639bcc75d47c0216b1be383c4a8ed4fac77c0d2ad737d8499a362f483f8fe39d1e86aaed578a9455dfc'))
	print(pvk_to_wif(bytes.fromhex("000000000000000000000000000000000000000000000001a838b13505b26867")))
	print(wif_to_pvk('5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ipCnYRNeQuRFKarWVVs'))

def privkey_to_pubkey(privkey: bytes) -> bytes:
	"""
	Zwraca klucz publiczny w formacie skompresowanym (33 bajty) dla krzywej secp256k1.
	"""
	if not isinstance(privkey, (bytes, bytearray)) or len(privkey) != 32:
		raise ValueError("privkey musi być dokładnie 32 bajtami")
	sk = ecdsa.SigningKey.from_string(privkey, curve=SECP256k1)
	vk = sk.get_verifying_key()
	return vk.to_string("compressed")


def pubkey_to_address(pubkey: bytes, *, hrp: str = DEFAULT_BECH32_HRP) -> str:
	"""
	Cosmos-like adres Bech32: bech32(hrp, convertbits(RIPEMD160(SHA256(pubkey)), 8->5)).
	"""
	if not isinstance(pubkey, (bytes, bytearray)):
		raise TypeError("pubkey musi być typu bytes")
	sha = hashlib.sha256(pubkey).digest()
	r160 = hashlib.new("ripemd160", sha).digest()  # 20 bajtów
	# Konwersja 8-bit -> 5-bit; pad=True aby uniknąć None
	five_bit = convertbits(r160, 8, 5, True)
	if five_bit is None:
		raise ValueError("convertbits nie powiodło się (wejście niepoprawne)")
	return bech32_encode(hrp, five_bit)


def privkey_to_address(privkey: bytes, *, hrp: str = DEFAULT_BECH32_HRP) -> str:
	"""
	Skrót: privkey -> pubkey (compressed) -> Bech32 address.
	"""
	return pubkey_to_address(privkey_to_pubkey(privkey), hrp=hrp)


def pvk_to_wif(z: bytes | str, *, compressed: bool = True) -> str:
	"""
	Zwraca WIF (Bitcoin mainnet) dla 32-bajtowego klucza prywatnego.
	- z: bytes (32) albo hex string (64 znaki)
	- compressed=True doda sufiks 0x01 przed obliczeniem checksumy
	"""
	if isinstance(z, str):
		try:
			key = bytes.fromhex(z)
		except ValueError as e:
			raise ValueError("z nie jest poprawnym hexem") from e
	else:
		key = bytes(z)

	if len(key) != 32:
		raise ValueError("klucz prywatny musi mieć 32 bajty")

	prefix_payload = b"\x80" + key + (b"\x01" if compressed else b"")
	# Używamy wbudowanego check-encode, zamiast ręcznie liczyć podwójne SHA256.
	return base58.b58encode_check(prefix_payload).decode("ascii")


def lines(path_like: str) -> int:
	"""
	Liczy linie w pliku bez wczytywania całości do pamięci.
	"""
	with open(path_like, "r", encoding="utf-8", errors="replace") as f:
		return sum(1 for _ in f)


def st(path_or_iterable: str | Iterable[str]) -> List[str]:
	"""
	Zwraca listę linii przyciętych z białych znaków.
	- Jeśli podasz ścieżkę (str), czyta z pliku.
	- Jeśli podasz iterowalne linii, przetwarza je wprost.
	"""
	if isinstance(path_or_iterable, str):
		with open(path_or_iterable, "r", encoding="utf-8", errors="replace") as f:
			return [line.strip() for line in f]
	else:
		return [line.strip() for line in path_or_iterable]


if __name__ == "__main__":
	# Krótkie sanity-checki (nie są to testy jednostkowe)
	ex_priv = bytes.fromhex("11" * 32)
	pub = privkey_to_pubkey(ex_priv)
	print("pub(compressed):", pub.hex())
	print("addr(bech32):", pubkey_to_address(pub, hrp=DEFAULT_BECH32_HRP))
	print("wif(compressed):", pvk_to_wif(ex_priv, compressed=True))




# --- Hashe i pomocnicze ---
def sha256(data: bytes) -> bytes:
	return hashlib.sha256(data).digest()

def ripemd160(data: bytes) -> bytes:
	return hashlib.new("ripemd160", data).digest()

def hash160(data: bytes) -> bytes:
	return ripemd160(sha256(data))

def b58check_encode(versioned_payload: bytes) -> str:
	check = sha256(sha256(versioned_payload))[:4]
	return base58.b58encode(versioned_payload + check).decode("ascii")

def int_to_bytes3(value: int, length: int | None = None) -> bytes:
	if value == 0 and not length:
		return b"\x00"
	if not length:
		length = (value.bit_length() + 7) // 8
	return value.to_bytes(length, "big")

def int_to_hex(n: int, hexdigits: int) -> str:
	return hex(n)[2:].zfill(hexdigits)

def int_to_hex2(n: int, hexdigits: int) -> str:
	h = hex(n)[2:]
	return '0' * (hexdigits - len(h)) + h

def int_to_pvk(x: int) -> str:
	return hex(x)[2:].zfill(64)

def growing_range(mid: int, x: int):
	start = mid - x
	end = mid + x
	rng = [0] * (x * 2 - 1)
	rng[::2], rng[1::2] = range(mid, end), range(mid - 1, start, -1)
	return rng


# --- Klucze i adresy (Bitcoin, mainnet P2PKH, prefix 0x00) ---
def privkey_to_pubkey(privkey: bytes, *, compressed: bool = True) -> bytes:
	"""
	Zwraca klucz publiczny (33 bajty skompresowany lub 65 bajtów nieskompresowany).
	"""
	if not isinstance(privkey, (bytes, bytearray)) or len(privkey) != 32:
		raise ValueError("privkey musi mieć dokładnie 32 bajty")
	sk = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	if compressed:
		prefix = b"\x03" if (vk.pubkey.point.y() & 1) else b"\x02"
		return prefix + int_to_bytes3(vk.pubkey.point.x(), 32)
	return b"\x04" + int_to_bytes3(vk.pubkey.point.x(), 32) + int_to_bytes3(vk.pubkey.point.y(), 32)

def decompress_pubkey(pk: bytes) -> bytes:
	"""
	Wejście: skompresowany klucz publiczny (33 bajty, prefix 0x02/0x03)
	Wyjście: nieskompresowany (65 bajtów, prefix 0x04)
	"""
	if not isinstance(pk, (bytes, bytearray)) or len(pk) != 33 or pk[0] not in (2, 3):
		raise ValueError("Oczekiwano skompresowanego klucza publicznego (33 bajty)")
	x = int.from_bytes(pk[1:], "big")
	alpha = (pow(x, 3, P) + 7) % P
	y = pow(alpha, (P + 1) // 4, P)  # sqrt mod P (dla secp256k1)
	if (y & 1) != (pk[0] & 1):
		y = (-y) % P
	return b"\x04" + int_to_bytes3(x, 32) + int_to_bytes3(y, 32)

def compressedToUncompressed(hex_compressed: str) -> str:
	"""
	Wejście HEX (skompresowany), wyjście HEX (nieskompresowany).
	"""
	pk = bytes.fromhex(hex_compressed)
	return decompress_pubkey(pk).hex()

def pubkey_to_p2pkh_address(pubkey: bytes) -> str:
	h160 = hash160(pubkey)
	return b58check_encode(b"\x00" + h160)

def pvk_bin_to_addr(pvk: bytes, *, compressed: bool = True) -> str:
	pub = privkey_to_pubkey(pvk, compressed=compressed)
	return pubkey_to_p2pkh_address(pub)

def getPublicKey(privkey: bytes) -> str:
	"""
	Zachowuję nazwę z oryginału, ale zwracam adres P2PKH (mainnet).
	"""
	return pvk_bin_to_addr(privkey, compressed=True)

def getWif(privkey: bytes, *, compressed: bool = True) -> str:
	"""
	WIF (mainnet). Jeśli compressed=True, doklejany jest bajt 0x01 przed sumą kontrolną.
	"""
	if len(privkey) != 32:
		raise ValueError("privkey musi mieć 32 bajty")
	payload = b"\x80" + privkey + (b"\x01" if compressed else b"")
	return b58check_encode(payload)

def hex_public_to_public_addresses(hex_publics: list[str]) -> tuple[str, str]:
	"""
	Wejście: [uncompressed_hex, compressed_hex]
	Zwraca: (addr_uncompressed, addr_compressed)
	"""
	uncompressed_hex, compressed_hex = hex_publics
	addr_uncompressed = pubkey_to_p2pkh_address(bytes.fromhex(uncompressed_hex))
	addr_compressed = pubkey_to_p2pkh_address(bytes.fromhex(compressed_hex))
	return addr_uncompressed, addr_compressed

def private_to_hex_publics(hex_private_key: str) -> tuple[str, str]:
	"""
	HEX priv -> (uncompressed_pub_hex, compressed_pub_hex)
	"""
	priv = bytes.fromhex(hex_private_key)
	pub_unc = privkey_to_pubkey(priv, compressed=False).hex().upper()
	pub_cmp = privkey_to_pubkey(priv, compressed=True).hex().upper()
	return pub_unc, pub_cmp


# --- (Opcjonalnie) proste operacje EC punktowe — zostawione dla zgodności nazw ---
def modinv(a: int, n: int = P) -> int:
	return pow(a, -1, n)

def ECadd(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
	L = ((b[1] - a[1]) * modinv(b[0] - a[0], P)) % P
	x = (L * L - a[0] - b[0]) % P
	y = (L * (a[0] - x) - a[1]) % P
	return x, y

def ECdouble(a: tuple[int, int]) -> tuple[int, int]:
	L = ((3 * a[0] * a[0]) * modinv(2 * a[1], P)) % P
	x = (L * L - 2 * a[0]) % P
	y = (L * (a[0] - x) - a[1]) % P
	return x, y

def EccMultiply(gen_point: tuple[int, int], scalar: int) -> tuple[int, int]:
	if scalar <= 0 or scalar >= N:
		raise ValueError("Invalid scalar/private key")
	Q = None
	Np = gen_point
	while scalar:
		if scalar & 1:
			Q = Np if Q is None else ECadd(Q, Np)
		Np = ECdouble(Np)
		scalar >>= 1
	return Q


# --- Demo / sanity-check ---
if __name__ == "__main__":
	# Testowy klucz (tylko do demonstracji!):
	priv_hex = "11" * 32
	priv = bytes.fromhex(priv_hex)

	# Pubkey
	pub_cmp = privkey_to_pubkey(priv, compressed=True)
	pub_unc = privkey_to_pubkey(priv, compressed=False)
	print("pub (compressed):", pub_cmp.hex())
	print("pub (uncompressed):", pub_unc.hex())

	# Adresy
	print("addr (P2PKH, compressed):", pubkey_to_p2pkh_address(pub_cmp))
	print("addr (P2PKH, uncompressed):", pubkey_to_p2pkh_address(pub_unc))

	# WIF
	print("WIF (compressed):", getWif(priv, compressed=True))
	print("WIF (uncompressed):", getWif(priv, compressed=False))

	# Dekompresja klucza skompresowanego
	print("decompress:", decompress_pubkey(pub_cmp).hex())

	# Funkcja kompatybilna z Twoją nazwą:
	print("getPublicKey (adres):", getPublicKey(priv))

	# EC multiply (sprawdzenie zgodności z ecdsa)
	Q = EccMultiply(GPOINT, int(priv_hex, 16))
	x_e, y_e = Q
	assert x_e.to_bytes(32, "big") == pub_unc[1:33]
	assert y_e.to_bytes(32, "big") == pub_unc[33:]
	print("EC multiply sanity: OK")

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

def _fast_count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def human(n):
	units = ['','K','M','G','T','P','E']
	i = 0
	x = float(n)
	while x >= 1000.0 and i < len(units)-1:
		x /= 1000.0
		i += 1
	return f"{x:.2f}{units[i]}"
