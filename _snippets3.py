#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Uwaga: zgodnie z preferencją — taby zamiast spacji.

import base58
import hashlib
import ecdsa

# --- Stałe secp256k1 ---
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
GPOINT = (Gx, Gy)


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
