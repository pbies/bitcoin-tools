#!/usr/bin/env python3
import bitcoin
import binascii
import base58
import hashlib

outfile = open("output.txt","wb")

with open("input.txt","r") as f:
	for line in f:
		x=line.rstrip('\n')
		ext=b'\x80'+binascii.unhexlify(x)
		wif=base58.b58encode_check(ext)
		#print(wif)
		outfile.write(wif+b' 0\n')

outfile.close()
