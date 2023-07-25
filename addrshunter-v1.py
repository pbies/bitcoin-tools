#!/usr/bin/python3

import sys

readlength=10*1024*1024

magic = b'name'
magiclen = len(magic)

if len(sys.argv) != 2:
	print("./{0} <filename>".format(sys.argv[0]))
	exit()

def bytes_to_int(bytes):
	return int.from_bytes(bytes,'big')

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
			key_offset = pos+magiclen
			cnt=bytes_to_int(data[key_offset:key_offset+1])
			key_data = data[key_offset+1:key_offset + cnt+1]
			print(key_data.decode('utf-8'))
			pos += 1

		if len(data) == readlength:
			f.seek(f.tell() - (32 + magiclen))
