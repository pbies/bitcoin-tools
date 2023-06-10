#!/usr/bin/env python3

import base58
import hashlib
import sys

o = open('output.txt','w',encoding="utf-8")

for c in range(256):
	data=[]
	data.append(c)
	st1='80'+hashlib.sha256(bytearray(data)).digest().hex()
	st2=bytes.fromhex(st1)
	st3=base58.b58encode_check(st2)
	o.write(st3.decode('utf-8')+' 0\n')
