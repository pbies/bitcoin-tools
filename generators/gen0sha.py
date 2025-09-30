#!/usr/bin/env python3

import base58

outfile = open('output.txt','wb')

for a in range(35):
	for b in range(256):
		for c in range(256):
			d=bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
			d.append(a)
			d.append(b)
			d.append(c)
			tmp=b'\x80'+d
			h=base58.b58encode_check(tmp)
			i=h+b' 0\n'
			outfile.write(i)

outfile.close()
