#!/usr/bin/env python3

o=open('crc32.txt','w')
for i in range(0,2**32):
	o.write(f'{hex(i)[2:].zfill(8)}\n')
