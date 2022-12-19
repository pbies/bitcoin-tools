#!/usr/bin/env python3
import binascii
import base58

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]
f.close()

outfile = open("output.txt","wb")
for x in content:
	first_decode=b""
	y=binascii.unhexlify(x)
	try:
		first_decode = base58.b58decode(y)
	except:
		pass
	private_key_full = binascii.hexlify(first_decode)
	private_key = private_key_full[2:-8]
	outfile.write(bytes.fromhex(private_key.decode('utf-8')))

outfile.close()
