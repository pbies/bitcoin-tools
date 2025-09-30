#!/usr/bin/env python3
import os

lines=100
chars=32

with open("output.txt", "wb") as f:
	for i in range(lines):
		for j in range(chars):
			c=os.urandom(1)
			if c!=b'\x0a':
				f.write(bytes(c))
		f.write(b'\x0a')
f.close()
