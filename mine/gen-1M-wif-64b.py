#!/usr/bin/env python3

import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode_check(hex);

def sha256(hex):
	return hashlib.sha256(hex).digest();

def to_wif(data):
	return b58(bytes.fromhex('80'+sha256(data).hex()));

o=open("wallet.txt","w")

for b1 in range(17):
	for b2 in range(256):
		for b3 in range(256):
			o.write(to_wif(bytes(61)+bytes([b1,b2,b3]))+' 0\n')
