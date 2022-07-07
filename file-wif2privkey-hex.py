#!/usr/bin/env python3

import hashlib
import base58
import binascii

with open("input.txt") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('output.txt','w')

for line in content:
	first_encode = base58.b58decode(line)
	private_key_full = binascii.hexlify(first_encode)
	private_key = private_key_full[2:-8]
	o.write(private_key.decode('utf-8'))
