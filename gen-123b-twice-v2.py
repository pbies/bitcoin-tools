#!/usr/bin/env python3

import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode_check(hex);

def sha256(hex):
	return hashlib.sha256(hex).digest();

def to_wif(data):
	return b58(bytes.fromhex('80'+sha256(sha256(data)).hex()));

o=open("import.txt","wb")

for b1 in range(256):
	o.write(to_wif(bytes([b1]))+b' 0\n')

for b1 in range(256):
	for b2 in range(256):
		o.write(to_wif(bytes([b1,b2]))+b' 0\n')
