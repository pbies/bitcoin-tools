#!/usr/bin/env python3

from tqdm import tqdm
import sys

def conv(x,y):
	prefix = '02' if y % 2 == 0 else '03'
	c = prefix+ hex(x)[2:].zfill(64)
	return c

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.read().splitlines()

for line in lines:
	try:
		x=int(line[2:66], 16)
		y=int(line[66:], 16)
		z=conv(x, y)
		outfile.write(z+'\n')
		outfile.flush()
	except:
		print(f'Error: {line}', file=sys.stderr)

print('\a', end='', file=sys.stderr)
