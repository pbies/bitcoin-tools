#!/usr/bin/env python3

import hashlib
import sys

o=open("output.bin","wb")

for i in range(256):
	o.write(chr(i)+"\n")
for i in range(256):
	for j in range(256):
		o.write(chr(i)+chr(j)+"\n")
for i in range(256):
	for j in range(256):
		for k in range(256):
			o.write(chr(i)+chr(j)+chr(k)+"\n")
