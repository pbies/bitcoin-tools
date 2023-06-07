#!/usr/bin/python3

import sys
import base58

readlength=10*1024*1024

magic = b'name\"'
magiclen = len(magic)
#magic2 = b'\x00'

chars=b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'

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
			#end_offset = data.find(magic2, key_offset)
			key_data = data[key_offset:key_offset+34]
			x=False
			for i in key_data:
				if i in chars:
					x=True
			if not x: print(key_data.decode('utf-8'))
			pos += 1

		if len(data) == readlength:
			f.seek(f.tell() - (32 + magiclen))
