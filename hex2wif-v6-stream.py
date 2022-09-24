#!/usr/bin/env python3
import bitcoin
import binascii
import base58
import hashlib
import sys

outfile = open(sys.argv[1]+'.wif',"wb")

with open(sys.argv[1],"r") as f:
	for line in f:
		x=line.rstrip('\n')
		ext=b'\x80'+binascii.unhexlify(x)
		wif=base58.b58encode_check(ext)
		#print(wif)
		outfile.write(wif+b' 0\n')

outfile.close()
