#!/usr/bin/env python3

import base58
import hashlib
import sys

f1 = open("in.txt","r")
f2 = open("out.txt","w")
count = 0

while True:
	line = f1.readline()

	line = line.strip()

	if not line:
		break

	line = line.strip()

	try:
		x=base58.b58decode_check(line)
	except:
		continue

	f2.write(base58.b58encode_check(x).decode('cp437')+" 0\n")
	count+=1

print(count)

f1.close()
f2.close()
