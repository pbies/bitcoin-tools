#!/usr/bin/env python3

from mnemonic import Mnemonic

mnemo = Mnemonic("english")

with open("input.txt") as f:
	lines = f.readlines()

lines = [x.strip() for x in lines]

o=open("output.txt","w")

for line in lines:
	try:
		pvk=mnemo.to_seed(line).hex()
		# print(pvk)
		o.write(pvk+'\n')
	except:
		continue
