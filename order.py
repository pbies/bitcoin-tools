#!/usr/bin/env python3
from bitcoin import *
from tqdm import tqdm

cnt=65536 # check this space from 1

with open("balances.txt","r") as f:
	content = f.readlines()

balances = [x.rstrip('\n') for x in content]

outfile = open("log.txt","w")

for a in tqdm(range(1,cnt), total=cnt, unit=" keys"):
	b=a.to_bytes(32,'big')
	c=privtoaddr(b)
	if c in balances:
		outfile.write(b.hex()+'\n')
		outfile.flush()
		print('Hit! Quitting...')
		quit()
