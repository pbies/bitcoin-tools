#!/usr/bin/env python3

# add " 0" at end of lines

import sys

with open("input.txt") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('output.txt','w')

for line in content:
	o.write(line + " 0\n")
