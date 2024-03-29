#!/usr/bin/env python3

# convert brainwallet to WIF

import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode_check(hex)

def sha256(hex):
	return hashlib.sha256(hex).digest()

def main():
	k = sha256(str(sys.argv[1]).encode('utf-8'))
	extend = '80' + k.hex()
	print(b58(bytes.fromhex(extend)).decode('utf-8'))

if __name__ == '__main__':
	main()
