#!/usr/bin/env python3

import hashlib
import sys

with open("list.txt","rb") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('list-sha256.txt','w')

for line in content:
	o.write(hashlib.sha256(line).hexdigest()+"\n")
