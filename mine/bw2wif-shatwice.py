#!/usr/bin/env python3

# many brainwallets to WIFs; sha256 twice

# pip3 install base58

import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode_check(hex)

def sha256(hex):
	return hashlib.sha256(hex).digest()

def main():
	with open("input.txt","rb") as f:
		content = f.readlines()

	content = [x.strip() for x in content]

	o = open('output.txt','w')

	for line in content:
		k = sha256(line)
		k = sha256(k)
		extend = '80' + k.hex()
		o.write(b58(bytes.fromhex(extend)).decode('utf-8') + " 0\n")

if __name__ == '__main__':
	main()
