#!/usr/bin/env python3
# (C) 2022 Piotr Biesiada

import sys

with open("list.txt","rb") as f:
	content = f.readlines()

with open("suf.txt","rb") as g:
	suf = g.readlines()

content = [x.rstrip(b'\n') for x in content]
suf = [x.rstrip(b'\n') for x in suf]

o = open('list-suf.txt','wb')

for line1 in content:
	for line2 in suf:
		o.write(line1+line2+b'\n')
		o.write(line2+line1+b'\n')
