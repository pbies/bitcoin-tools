#!/usr/bin/env python3

import sys
import base58

readlength=10*1024*1024

magic = b'name\"'
magiclen = len(magic)

def b58c(hex):
	return base58.b58encode_check(hex)

if len(sys.argv) != 2:
	print("./{0} <filename>".format(sys.argv[0]))
	exit()

with open(sys.argv[1], "rb") as f:
	while True:
		data = f.read(readlength)
		if not data:
			break

		pos = 0
		while True:
			pos = data.find(magic, pos)
			if pos == -1:
				break
			key_offset = pos + magiclen
			key_data = data[key_offset:key_offset + 34]
			if b'\x01' in key_data:
				pos += 1
				continue
			if b'name"' in key_data:
				pos += 1
				continue
			print(key_data.decode('utf-8'))
			pos += 1

		if len(data) == readlength:
			f.seek(f.tell() - (32 + magiclen))
