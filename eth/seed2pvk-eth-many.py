#!/usr/bin/env python3

# https://wolovim.medium.com/ethereum-201-hd-wallets-11d0c93c87f7

import binascii
import hmac
import hashlib
from tqdm import tqdm

# need to edit /etc/ssl/openssl.cnf
# https://stackoverflow.com/questions/72409563/unsupported-hash-type-ripemd160-with-hashlib-in-python

# the HMAC-SHA512 `key` and `data` must be bytes:

from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key

SECP256k1_GEN = SECP256k1.generator

def serialize_curve_point(K):
	x, y = K.x(), K.y()
	if y & 1:
		return b'\x03' + x.to_bytes(32, 'big')
	else:
		return b'\x02' + x.to_bytes(32, 'big')

def curve_point_from_int(k):
	return Public_key(SECP256k1_GEN, SECP256k1_GEN * k).point

def fingerprint_from_private_key(k):
	K = curve_point_from_int(k)
	K_compressed = serialize_curve_point(K)
	identifier = hashlib.new(
		'ripemd160',
		hashlib.sha256(K_compressed).digest(),
	).digest()
	return identifier[:4]

SECP256k1_ORD = SECP256k1.order

def derive_ext_private_key(private_key, chain_code, child_number):
	if child_number >= 2 ** 31:
		 # Generate a hardened key
		 data = b'\x00' + private_key.to_bytes(32, 'big')
	else:
		 # Generate a non-hardened key
		 p = curve_point_from_int(private_key)
		 data = serialize_curve_point(p)
	data += child_number.to_bytes(4, 'big')
	hmac_bytes = hmac.new(chain_code, data, hashlib.sha512).digest()
	L, R = hmac_bytes[:32], hmac_bytes[32:]
	L_as_int = int.from_bytes(L, 'big')
	child_private_key = (L_as_int + private_key) % SECP256k1_ORD
	child_chain_code = R
	return (child_private_key, child_chain_code)

o=open('output.txt','w')
cnt=sum(1 for line in open("input.txt", 'r'))

for i in tqdm(open('input.txt'),total=cnt):
	seed=i.strip()
	seed_bytes = binascii.unhexlify(seed)
	I = hmac.new(b'Bitcoin seed', seed_bytes, hashlib.sha512).digest()
	L, R = I[:32], I[32:]
	master_private_key = int.from_bytes(L, 'big')
	master_chain_code = R

	path_numbers = (2147483692, 2147483708, 2147483648, 0, 0)
	depth = 0
	parent_fingerprint = None
	child_number = None
	private_key = master_private_key
	chain_code = master_chain_code
	for i in path_numbers:
		depth += 1
		child_number = i
		parent_fingerprint = fingerprint_from_private_key(private_key)
		private_key, chain_code = derive_ext_private_key(private_key,chain_code,child_number)
		o.write(hex(private_key)+'\n')
