#!/usr/bin/env python3

from cryptos import *
from Crypto import PublicKey
from cryptotools.BTC import PrivateKey, send
from tqdm import tqdm
import base58
import binascii
import bitcoin
import ecdsa
import hashlib
import os
import sys

def sha256(data):
	digest = hashlib.new("sha256")
	digest.update(data)
	return digest.digest()

def ripemd160(x):
	d = hashlib.new("ripemd160")
	d.update(x)
	return d.digest()

def b58(data):
	B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
	if data[0] == 0:
		return "1" + b58(data[1:])
	x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
	ret = ""
	while x > 0:
		ret = B58[x % 58] + ret
		x = x // 58
	return ret

ACURVE = 0
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
GPOINT = (Gx, Gy)
PCURVE = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1

class Point:
	def __init__(self,
		x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
		y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
		p=2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1):
		self.x = x
		self.y = y
		self.p = p

	def __add__(self, other):
		return self.__radd__(other)

	def __mul__(self, other):
		return self.__rmul__(other)

	def __rmul__(self, other):
		n = self
		q = None

		for i in range(256):
			if other & (1 << i):
				q = q + n
			n = n + n

		return q

	def __radd__(self, other):
		if other is None:
			return self
		x1 = other.x
		y1 = other.y
		x2 = self.x
		y2 = self.y
		p = self.p

		if self == other:
			l = pow(2 * y2 % p, p-2, p) * (3 * x2 * x2) % p
		else:
			l = pow(x1 - x2, p-2, p) * (y1 - y2) % p

		newX = (l ** 2 - x2 - x1) % p
		newY = (l * x2 - l * newX - y2) % p

		return Point(newX, newY)

	def toBytes(self):
		x = self.x.to_bytes(32, "big")
		y = self.y.to_bytes(32, "big")
		return b"\x04" + x + y

def getPublicKey(privkey):
	SPEC256k1 = Point()
	pk = int.from_bytes(privkey, "big")
	hash160 = ripemd160(sha256((SPEC256k1 * pk).toBytes()))
	address = b"\x00" + hash160
	address = b58(address + sha256(sha256(address))[:4])
	return address

def getWif(privkey):
	wif = b"\x80" + privkey
	wif = b58(wif + sha256(sha256(wif))[:4])
	return wif

def decompress_pubkey(pk):
	x = int.from_bytes(pk[1:33], byteorder='big')
	y_sq = (pow(x, 3, p) + 7) % p
	y = pow(y_sq, (p + 1) // 4, p)
	if y % 2 != pk[0] % 2:
		y = p - y
	y = y.to_bytes(32, byteorder='big')
	return b'\x04' + pk[1:33] + y

def int_to_bytes3(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def pvk_bin_to_addr(pvk):
	SPEC256k1 = Point()
	pk = int.from_bytes(pvk, "big")
	hash160 = ripemd160(sha256((SPEC256k1 * pk).toBytes()))
	address = b"\x00" + hash160
	return base58.b58encode(address+sha256(sha256(address))[:4]).decode()

def compressedToUncompressed(compressed_key):
	p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
	y_parity = int(compressed_key[:2]) - 2
	x = int(compressed_key[2:], 16)
	a = (pow(x, 3, p) + 7) % p
	y = pow(a, (p+1)//4, p)
	if y % 2 != y_parity:
		y = -y % p
	uncompressed_key = '04{:x}{:x}'.format(x, y)
	return uncompressed_key

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def hex_public_to_public_addresses(hex_publics):
	uncompressed = hex_publics[0]
	public_key_hashC_uncompressed = "00" + sha_ripe_digest(uncompressed)
	checksum = sha256_get_checksum(public_key_hashC_uncompressed)
	PublicKeyChecksumC = public_key_hashC_uncompressed + checksum
	public_address_uncompressed = "1" + b58encode(PublicKeyChecksumC, 33)
	print("Public address uncompressed:\t", public_address_uncompressed)

	compressed = hex_publics[1]
	PublicKeyVersionHashD = "00" + sha_ripe_digest(compressed)
	compressed_checksum = sha256_get_checksum(PublicKeyVersionHashD)
	PublicKeyChecksumC = PublicKeyVersionHashD + compressed_checksum
	public_address_compressed = "1" + b58encode(PublicKeyChecksumC, 33)
	print("Public address compressed:\t", public_address_compressed)
	return public_address_uncompressed, public_address_compressed

def modinv(a: int, n: int = PCURVE):
	lm, hm = 1, 0
	resto = a % n
	high = n
	while resto > 1:
		ratio = high // resto
		nm = hm - lm * ratio
		new = high - resto * ratio
		lm, resto, hm, high = nm, new, lm, resto
	return lm % n

def ECadd(a, b):
	LamAdd = ((b[1] - a[1]) * modinv(b[0] - a[0], PCURVE)) % PCURVE
	x = (LamAdd * LamAdd - a[0] - b[0]) % PCURVE
	y = (LamAdd * (a[0] - x) - a[1]) % PCURVE
	return x, y

def ECdouble(a):
	Lam = ((3 * a[0] * a[0] + ACURVE) * modinv((2 * a[1]), PCURVE)) % PCURVE
	x = (Lam * Lam - 2 * a[0]) % PCURVE
	y = (Lam * (a[0] - x) - a[1]) % PCURVE
	return x, y

def EccMultiply(gen_point: tuple, scalar_hex: int):
	if scalar_hex == 0 or scalar_hex >= N:
		raise Exception("Invalid Scalar/Private Key")
	ScalarBin = str(bin(scalar_hex))[2:]
	Q = gen_point
	for i in range(1, len(ScalarBin)):
		Q = ECdouble(Q)
		if ScalarBin[i] == "1":
			Q = ECadd(Q, gen_point)
	return Q

def private_to_hex_publics(hex_private_key: hex):
	public_key = EccMultiply(GPOINT, hex_private_key)
	public_uncompressed = f"04{hex(public_key[0])[2:].upper()}{hex(public_key[1])[2:].upper()}"

	if public_key[1] % 2 == 1:
		public_compressed = ("03" + str(hex(public_key[0])[2:]).zfill(64).upper())
	else:
		public_compressed = ("02" + str(hex(public_key[0])[2:]).zfill(64).upper())
	return public_uncompressed, public_compressed

def decode(cls, key: bytes) -> 'PublicKey':
	if key.startswith(b'\x04'):
		assert len(key) == 65, 'An uncompressed public key must be 65 bytes long'
		x, y = bytes_to_int(key[1:33]), bytes_to_int(key[33:])
	else:
		assert len(key) == 33, 'A compressed public key must be 33 bytes long'
		x = bytes_to_int(key[1:])
		root = modsqrt(CURVE.f(x), P)
		if key.startswith(b'\x03'):
			y = root if root % 2 == 1 else -root % P
		elif key.startswith(b'\x02'):
			y = root if root % 2 == 0 else -root % P
		else:
			assert False, 'Wrong key format'

	return cls(Point(x, y))

def encode(self, compressed=False) -> bytes:
	if compressed:
		if self.y & 1:
			return b'\x03' + int_to_bytes(self.x).rjust(32, b'\x00')
		else:
			return b'\x02' + int_to_bytes(self.x).rjust(32, b'\x00')
	return b'\x04' + int_to_bytes(self.x).rjust(32, b'\x00') + int_to_bytes(self.y).rjust(32, b'\x00')

def growing_range(mid,x): # x = range +-
	start=mid-x
	end=mid+x
	rng = [0] * (x*2-1)
	rng[::2], rng[1::2] = range(mid, end), range(mid-1, start, -1)
	return rng

def int_to_hex(n, hexdigits):
	return hex(n)[2:].zfill(hexdigits)

def int_to_pvk(x):
	return hex(x)[2:].zfill(64)

def int_to_hex2(n, hexdigits):
	h=hex(n)[2:]
	return '0'*(hexdigits-len(h))+h
