#!/usr/bin/env python3

import base58
import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import random
import re
import struct
import unittest
# import utils

def bytes_to_str(bytes):
	return bytes.decode("utf-8")

def bytes_to_int(bytes):
	result = 0
	for b in bytes:
		result = result * 256 + ordsix(b)
	return result

def bytes_to_int2(bytes):
	return int.from_bytes(bytes,"big")

def bytes_to_hex(bytes):
	return bytes.hex()

def count_lines(file):
	return sum(1 for line in open(file, 'r'))

def hex_to_bytes(hex):
	return bytes.fromhex(hex)

def hex_to_int(hex):
	return int(hex, 16)

def int_to_bytes(s):
	return chr(s).encode('utf-8')

def int_to_bytes2(s):
	return bytearray([s])

def int_to_bytes(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return str(bytearray(result))

def int_to_bytes(number):
	# 32 = number of zeros preceding
	return number.to_bytes(32,'big')

def int_to_bytes(number):
	return str.encode(str(number))

def int_to_str(number):
	return str(number)

def key_to_addr(s):
	return pubKeyToAddr(privateKeyToPublicKey(s))

def privatekey_to_wif(key_hex):
	return base58.b58encode_check(0x80, key_hex.decode('hex'))

def privatekey_to_publickey(s):
	sk = ecdsa.SigningKey.from_string(s.decode('hex'), curve=ecdsa.SECP256k1)
	vk = sk.verifying_key
	return ('\04' + sk.verifying_key.to_string()).encode('hex')

def pubkey_to_addr(s):
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(hashlib.sha256(s.decode('hex')).digest())
	return base58.b58encode_check(ripemd160.digest())

def reverse_string(s):
	return s[::-1]

def str_to_bytes(text):
	return str.encode(text)

def str_to_hex(text):
	return "".join(x.encode('hex') for x in text)

def wif_to_privatekey(s):
	b = base58.bs58decode_check(s)
	return b.encode('hex')
