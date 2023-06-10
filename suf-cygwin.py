#!/usr/bin/env python3

import sys

with open("list.txt","rb") as f:
	content = f.readlines()

with open("suf.txt","rb") as g:
	suf = g.readlines()

content = [x.strip() for x in content]
suf = [x.strip() for x in suf]

o = open('list-suf.txt','wb')

for line1 in content:
	for line2 in suf:
		o.write(line1+line2+"\n")
		o.write(line2+line1+"\n")
