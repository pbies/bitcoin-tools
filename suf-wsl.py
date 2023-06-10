#!/usr/bin/env python3

import sys

with open("list.txt","rb") as f:
	content = f.readlines()

with open("suf.txt","rb") as g:
	suf = g.readlines()

content = [x.strip() for x in content]
suf = [x.strip() for x in suf]

o = open('list-suf.txt','w')

for line1 in content:
	for line2 in suf:
		o.write(line1.decode()+"\n")
		o.write(line2.decode()+"\n")
		o.write(line1.decode()+line2.decode()+"\n")
		o.write(line2.decode()+line1.decode()+"\n")
