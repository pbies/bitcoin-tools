#!/usr/bin/env python3

import sys

with open("list.txt","rb") as f:
	passwds = f.readlines()

with open("suf.txt","rb") as g:
	suf = g.readlines()

passwds = [x.rstrip(b'\n') for x in passwds]
suf = [x.rstrip(b'\n') for x in suf]

o = open('list-suf.txt','wb')

for line1 in passwds:
	for line2 in suf:
		o.write(line1+line2+b"\n")
		o.write(line2+line1+b"\n")
