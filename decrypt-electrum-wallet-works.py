#!/usr/bin/env python3

import os
os.system('cls||clear')

from Crypto.Util.Padding import unpad, pad
from Crypto.Cipher import AES
from ctypes import create_string_buffer, c_size_t, byref
from ecc_fast import _libsecp256k1, SECP256K1_EC_UNCOMPRESSED
from typing import Union, Optional, Tuple
import base64
import hashlib
import hmac
import json
import pprint
import pyaes
import zlib
from random import *

HAS_PYAES = True
wallet_path = "./default_wallet"
password = b"123456"
CURVE_ORDER = 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_BAAEDCE6_AF48A03B_BFD25E8C_D0364141
global ss

class InvalidECPointException(Exception):
	pass

def string_to_number(b: bytes) -> int:
	return int.from_bytes(b, byteorder='big', signed=False)

def normalize_secret_bytes(privkey_bytes: bytes) -> bytes:
	scalar = string_to_number(privkey_bytes) % CURVE_ORDER
	if scalar == 0:
		raise Exception('invalid EC private key scalar: zero')
	privkey_32bytes = int.to_bytes(scalar, length=32, byteorder='big', signed=False)
	return privkey_32bytes

def from_arbitrary_size_secret(privkey_bytes: bytes) -> bytes:
	return normalize_secret_bytes(privkey_bytes)

def get_eckey_from_password(password):
	if password is None:
		password = b""
	secret = hashlib.pbkdf2_hmac('sha512', password, b'', iterations=1024)
	ec_key = from_arbitrary_size_secret(secret)
	return ec_key

def _get_encryption_magic():
	return b'BIE1'

def _x_and_y_from_pubkey_bytes(pubkey: bytes) -> Tuple[int, int]:
	assert isinstance(pubkey, bytes), f'pubkey must be bytes, not {type(pubkey)}'
	pubkey_ptr = create_string_buffer(64)
	ret = _libsecp256k1.secp256k1_ec_pubkey_parse(
		_libsecp256k1.ctx, pubkey_ptr, pubkey, len(pubkey))
	if 1 != ret:
		raise Exception(f'public key could not be parsed or is invalid: {pubkey.hex()!r}')

	pubkey_serialized = create_string_buffer(65)
	pubkey_size = c_size_t(65)
	_libsecp256k1.secp256k1_ec_pubkey_serialize(
		_libsecp256k1.ctx, pubkey_serialized, byref(pubkey_size), pubkey_ptr, SECP256K1_EC_UNCOMPRESSED)
	pubkey_serialized = bytes(pubkey_serialized)
	assert pubkey_serialized[0] == 0x04, pubkey_serialized
	x = int.from_bytes(pubkey_serialized[1:33], byteorder='big', signed=False)
	y = int.from_bytes(pubkey_serialized[33:65], byteorder='big', signed=False)
	return x, y

def is_secret_within_curve_range(secret: Union[int, bytes]) -> bool:
	if isinstance(secret, bytes):
		secret = string_to_number(secret)
	return 0 < secret < CURVE_ORDER

def hmac_oneshot(key: bytes, msg: bytes, digest) -> bytes:
	if hasattr(hmac, 'digest'):
		return hmac.digest(key, msg, digest)
	else:
		return hmac.new(key, msg, digest).digest()

def aes_decrypt_with_iv(key: bytes, iv: bytes, data: bytes) -> bytes:
	cipher = AES.new(key[:32], AES.MODE_CBC, iv=iv)
	decrypted = cipher.decrypt(data)
	try:
		return unpad(decrypted, AES.block_size)
	except ValueError:
		return decrypted  # Return raw data if unpadding fails

class ECPubkey(object):
	def __init__(self, b: Optional[bytes]):
		if b is not None:
			assert isinstance(b, (bytes, bytearray)), f'pubkey must be bytes-like, not {type(b)}'
			if isinstance(b, bytearray):
				b = bytes(b)
			self.x, self.y = _x_and_y_from_pubkey_bytes(b)
		else:
			self.x, self.y = None, None

	def _from_libsecp256k1_pubkey_ptr(pubkey) -> 'ECPubkey':
		pubkey_serialized = create_string_buffer(65)
		pubkey_size = c_size_t(65)
		_libsecp256k1.secp256k1_ec_pubkey_serialize(
			_libsecp256k1.ctx, pubkey_serialized, byref(pubkey_size), pubkey, SECP256K1_EC_UNCOMPRESSED)
		return ECPubkey(bytes(pubkey_serialized))

	def _to_libsecp256k1_pubkey_ptr(self):
		"""pointer to `secp256k1_pubkey` C struct"""
		pubkey_ptr = create_string_buffer(64)
		pk_bytes = self.get_public_key_bytes(compressed=False)
		ret = _libsecp256k1.secp256k1_ec_pubkey_parse(
			_libsecp256k1.ctx, pubkey_ptr, pk_bytes, len(pk_bytes))
		if 1 != ret:
			raise Exception(f'public key could not be parsed or is invalid: {pk_bytes.hex()!r}')
		return pubkey_ptr

	def is_at_infinity(self) -> bool:
		return self == POINT_AT_INFINITY

	def __mul__(self, other: int):
		if not isinstance(other, int):
			raise TypeError('multiplication not defined for ECPubkey and {}'.format(type(other)))

		other %= CURVE_ORDER
		if self.is_at_infinity() or other == 0:
			return POINT_AT_INFINITY
		pubkey = self._to_libsecp256k1_pubkey_ptr()

		ret = _libsecp256k1.secp256k1_ec_pubkey_tweak_mul(_libsecp256k1.ctx, pubkey, other.to_bytes(32, byteorder="big"))
		if not ret:
			return POINT_AT_INFINITY
		return ECPubkey._from_libsecp256k1_pubkey_ptr(pubkey)

	def get_public_key_bytes(self, compressed=True) -> bytes:
		x = int.to_bytes(self.x, length=32, byteorder='big', signed=False)
		y = int.to_bytes(self.y, length=32, byteorder='big', signed=False)
		if compressed:
			header = b'\x03' if self.y & 1 else b'\x02'
			return header + x
		else:
			header = b'\x04'
			return header + x + y

GENERATOR = ECPubkey(bytes.fromhex(
	'0479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'
	'483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8'))
POINT_AT_INFINITY = ECPubkey(None)

class ECPrivkey(ECPubkey):
	def __init__(self, privkey_bytes: bytes):
		if len(privkey_bytes) != 32:
			raise Exception(f'unexpected size for secret. should be 32 bytes, not {len(privkey_bytes)}')
		global ss
		ss = string_to_number(privkey_bytes)
		if not is_secret_within_curve_range(ss):
			raise InvalidECPointException('Invalid secret scalar (not within curve order)')
		self.secret_scalar = ss

		pubkey = GENERATOR * ss
		super().__init__(pubkey.get_public_key_bytes(compressed=False))

	@staticmethod
	def generate_random_key() -> 'ECPrivkey':
		randint = randrange(CURVE_ORDER)
		ephemeral_exponent = int.to_bytes(randint, length=32, byteorder='big', signed=False)
		return ECPrivkey(ephemeral_exponent)

	@staticmethod
	def decrypt_message(encrypted: bytes, magic: bytes = b'QklF') -> bytes:
		if len(encrypted) < 85:
			raise Exception(f'invalid ciphertext: length = {len(encrypted)}')
		
		magic_found = encrypted[:4]
		ephemeral_pubkey_bytes = encrypted[4:37]
		ciphertext = encrypted[37:-32]
		mac = encrypted[-32:]
		
		if magic_found != magic:
			raise Exception(f'invalid ciphertext: invalid magic bytes. Expected {magic.hex()}, got {magic_found.hex()}')
		
		try:
			ephemeral_pubkey = ECPubkey(ephemeral_pubkey_bytes)
		except Exception as e:
			raise Exception('invalid ciphertext: invalid ephemeral pubkey') from e
			
		ecdh_key = ephemeral_pubkey.get_public_key_bytes(compressed=True)
		key = hashlib.sha512(ecdh_key).digest()
		iv, key_e, key_m = key[0:16], key[16:32], key[32:]
		
		if mac != hmac_oneshot(key_m, encrypted[:-32], hashlib.sha256):
			raise Exception('InvalidPassword')
			
		return aes_decrypt_with_iv(key_e, iv, ciphertext)

	def electrum_kdf(password: bytes, salt: bytes) -> bytes:
		"""Electrum's key derivation function."""
		return hashlib.pbkdf2_hmac('sha512', password, b'', iterations=1024)

def decrypt_wallet(filename: str, password: bytes) -> dict:
	"""Decrypt an Electrum wallet file."""
	with open(filename, 'rb') as f:
		encrypted = base64.b64decode(f.read())

	magic_found = encrypted[:4]
	#print(f'magic_found = {magic_found}')
	if magic_found != _get_encryption_magic():
		raise Exception('Invalid wallet format (magic bytes mismatch)')
	
	ephemeral_pubkey_bytes = encrypted[4:37]
	ciphertext = encrypted[37:-32]
	mac = encrypted[-32:]

	try:
		ephemeral_pubkey = ECPubkey(ephemeral_pubkey_bytes)
	except Exception as e:
		raise Exception(f'Invalid ephemeral pubkey: {e}')

	# Derive the decryption key from password
	privkey = ECPrivkey(get_eckey_from_password(password))
	
	# Perform ECDH: privkey * ephemeral_pubkey
	ecdh_point = ephemeral_pubkey * privkey.secret_scalar
	ecdh_key = ecdh_point.get_public_key_bytes(compressed=True)
	
	# Derive AES key material
	key = hashlib.sha512(ecdh_key).digest()
	iv, key_e, key_m = key[0:16], key[16:32], key[32:]
	
	# Verify MAC
	calculated_mac = hmac_oneshot(key_m, encrypted[:-32], hashlib.sha256)
	if not hmac.compare_digest(mac, calculated_mac):
		raise Exception('HMAC verification failed - wrong password or corrupted file')
	
	# Decrypt
	decrypted = aes_decrypt_with_iv(key_e, iv, ciphertext)
	try:
		decomp = zlib.decompress(decrypted)
		return decomp
	except zlib.error as e:
		raise Exception("Decompression failed") from e
	except json.JSONDecodeError as e:
		raise Exception("Invalid JSON format") from e

def main():
	# try:
	wallet_data = decrypt_wallet(wallet_path, password)
	#print("Successfully decrypted wallet:")
	y=json.loads(wallet_data)
	#x=json.dumps(y, indent=2)
	pprint.pprint(y)

if __name__ == "__main__":
	main()
