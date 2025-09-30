#!/usr/bin/env python3

# generate 2 bytes 0-255, convert them to WIFs

import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode_check(hex)

def sha256(hex):
	return hashlib.sha256(hex).digest()

def main():
	for x in range(256):
		for y in range(256):
			k = sha256(bytearray([x,y]))
			extend = '80' + k.hex()
			print(b58(bytes.fromhex(extend)).decode('utf-8')+' 0')
			#print(chr(y),end='')

if __name__ == '__main__':
	main()
