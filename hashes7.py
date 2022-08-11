#!/usr/bin/env python3

import hashlib
import sys

o = open('output.txt','w')

with open("input.txt","rb") as i:
	for line in i:
		l=line.rstrip(b'\n')
		o.write(hashlib.md5(l).hexdigest()+"\n")
		o.write(hashlib.sha1(l).hexdigest()+"\n")
		o.write(hashlib.sha256(l).hexdigest()+"\n")
