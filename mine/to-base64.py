#!/usr/bin/env python3

import hashlib
import base64
import sys

o = open('output.txt','w')

with open("input.txt","rb") as i:
	for line in i:
		l=line.rstrip(b'\n')
		o.write(base64.b64encode(line).decode('ascii')+'\n')
