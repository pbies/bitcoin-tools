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

correct=[33,34,42]

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
			cnt=bytes_to_int(data[key_offset:key_offset+1])
			if cnt in correct:
				key_data = data[key_offset+1:key_offset + cnt+1]
				if b'\n' in key_data or b'\x0d' in key_data or b'\x00' in key_data:
					pos += 1
					continue
				try:
					print(key_data.decode('utf-8'))
				except:
					pass
			pos += 1

		if len(data) == readlength:
			f.seek(f.tell() - (32 + magiclen))
