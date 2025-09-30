#!/usr/bin/env python3

import hashlib
import sys

with open("output.bin","rb") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('output-sha256.txt','w')

for line in content:
	o.write(hashlib.sha256(line).hexdigest()+"\n")
