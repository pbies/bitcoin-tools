#!/usr/bin/env python3

import sys

with open("wallet.txt") as f:
    content = f.readlines()

content = [x.strip() for x in content]

o = open('output.txt','w')

for line in content:
    o.write(line + " 0\n")
