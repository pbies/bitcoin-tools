#!/usr/bin/env python3

import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode_check(hex);

def sha256(hex):
	return hashlib.sha256(hex).digest();

def to_wif_sha_once(data):
	return b58(bytes.fromhex('80'+sha256(data).hex()));

def to_wif_sha_twice(data):
	return b58(bytes.fromhex('80'+sha256(sha256(data)).hex()));

for i in range(256):
	print(to_wif_sha_once(i.to_bytes(1,'big')).decode('utf-8')+' 0');

for i in range (65536):
	print(to_wif_sha_once(i.to_bytes(2,'big')).decode('utf-8')+' 0');

for i in range(256):
	print(to_wif_sha_twice(i.to_bytes(1,'big')).decode('utf-8')+' 0');

for i in range (65536):
	print(to_wif_sha_twice(i.to_bytes(2,'big')).decode('utf-8')+' 0');
