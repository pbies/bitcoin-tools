#!/usr/bin/env python3

from bitcoin import *
import os

with open("balances.txt","r") as f:
	content = f.readlines()

balances = [x.rstrip('\n') for x in content]

outfile = open("log.txt","a")

print('Start!')

while True:
	print('.',end='',flush=True)
	b=os.urandom(32)
	c=privtoaddr(b)
	if c in balances:
		outfile.write(b.hex()+'\n')
		outfile.flush()
		print('Hit! Quitting...')
		quit()
