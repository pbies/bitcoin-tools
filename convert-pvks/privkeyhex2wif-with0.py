#!/usr/bin/env python3

import binascii, hashlib, base58, sys

arq = open('output.txt', 'w')

def convert(z):
	private_key_static = z
	extended_key = "80"+private_key_static
	first_sha256 = hashlib.sha256(binascii.unhexlify(extended_key)).hexdigest()
	second_sha256 = hashlib.sha256(binascii.unhexlify(first_sha256)).hexdigest()
	final_key = extended_key+second_sha256[:8]
	WIF = base58.b58encode(binascii.unhexlify(final_key)).decode('utf-8')
	arq.write("%s 0\n" % WIF)

with open("input.txt") as file:
	for line in file:
		convert(str.strip(line))
