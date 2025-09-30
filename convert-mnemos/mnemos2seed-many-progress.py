#!/usr/bin/env python3

from mnemonic import Mnemonic
from tqdm import tqdm

mnemo = Mnemonic("english")

with open("input.txt") as f:
	lines = f.readlines()

lines = [x.strip() for x in lines]
cnt=len(lines)

o=open("output.txt","w")

for line in tqdm(lines,total=cnt):
	try:
		pvk=mnemo.to_seed(line).hex()
		# print(pvk)
		o.write(pvk+'\n')
	except:
		continue
