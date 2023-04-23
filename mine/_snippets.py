import base58
import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import random
import re
import struct
import unittest
import utils

def privateKeyToWif(key_hex):	
	return base58.b58encode_check(0x80, key_hex.decode('hex'))

def wifToPrivateKey(s):
	b = base58.bs58decode_check(s)
	return b.encode('hex')

def privateKeyToPublicKey(s):
	sk = ecdsa.SigningKey.from_string(s.decode('hex'), curve=ecdsa.SECP256k1)
	vk = sk.verifying_key
	return ('\04' + sk.verifying_key.to_string()).encode('hex')

def keyToAddr(s):
	return pubKeyToAddr(privateKeyToPublicKey(s))

def pubKeyToAddr(s):
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(hashlib.sha256(s.decode('hex')).digest())
	return base58.b58encode_check(ripemd160.digest())

def intToBytes(s):
	return chr(s).encode('utf-8')

def intToBytes2(s):
	return bytearray([s])

def countLines(file):
	return sum(1 for line in open(file, 'r'))

def reverseString(s):
	return s[::-1]
