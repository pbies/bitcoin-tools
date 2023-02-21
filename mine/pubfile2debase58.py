#!/usr/bin/env python3

import base58
import hashlib
import sys

with open("04uniq.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('05debase58.txt','wb')

for line in content:
	o.write(base58.b58decode_check(line)+b"\n")
