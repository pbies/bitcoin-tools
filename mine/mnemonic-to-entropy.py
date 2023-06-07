#!/usr/bin/env python3

from mnemonic import Mnemonic

mnemo = Mnemonic("english")

with open("input.txt") as f:
	lines = f.readlines()

lines = [x.strip() for x in lines]

o=open("output.txt","w")

for line in lines:
	try:
		print(mnemo.to_entropy(line).hex())
		o.write(mnemo.to_entropy(line).hex()+'\n')
	except:
		continue
