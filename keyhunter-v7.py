#!/usr/bin/env python3

import sys
import base58

readlength=10*1024*1024

magic = b'\x01\x30\x82\x01\x13\x02\x01\x01\x04\x20'
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
			key_data = b"\x80" + data[key_offset:key_offset + 32]
			print(b58c(key_data).decode('utf-8'))
			pos += 1

		if len(data) == readlength:
			f.seek(f.tell() - (32 + magiclen))

print('\a', end='', file=sys.stderr)
