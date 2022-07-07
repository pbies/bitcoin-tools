#!/usr/bin/env python3
# private hex bitcoin btc key to wif wallet import format
import base58
import hashlib
import sys

def b58(hex):
	return base58.b58encode(hex)

def sha256(hex):
	return hashlib.sha256(hex).digest()

def main():
	k = sha256(str(sys.argv[1]).encode('utf-8'))
	extend = '80' + k.hex()
	sha1 = sha256(bytes.fromhex(extend))
	sha2 = sha256(sha1)
	print(b58(bytes.fromhex(extend) + sha2[:4]).decode('utf-8'))

if __name__ == '__main__':
	main()
