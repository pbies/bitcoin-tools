#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
import hashlib, base58
import sys

if len(sys.argv)<4:
	print(f'Usage: {sys.argv[0]} patterns_file search_in_file output_file')
	sys.exit(1)

patt=open(sys.argv[1],'r').read().splitlines()
cnt=len(patt)
print(f'Searching for {cnt} patterns...')
infile=open(sys.argv[2],'r')
outfile=open(sys.argv[3],'w')

c=0
r=0

while True:
	wif1=infile.readline().rstrip()
	if not wif1:
		break
	wif2=infile.readline().rstrip()
	adr1=infile.readline().rstrip()
	adr2=infile.readline().rstrip()
	adr3=infile.readline().rstrip()
	adr4=infile.readline().rstrip()
	adr5=infile.readline().rstrip()
	adr6=infile.readline().rstrip()
	empty=infile.readline().rstrip()

	tmp=[wif1,wif2,adr1,adr2,adr3,adr4,adr5,adr6]

	for x in patt:
		if x in tmp:
			patt.remove(x)
			outfile.write('\n'.join(tmp)+'\n\n')
			outfile.flush()
			r=r+1

	c=c+1
	if c%10_000==0:
		print(f'Found: {r} ; Progress: {c}', end='\r')

print(f'Found: {r} ; Progress: {c}')

print('\a', end='', file=sys.stderr)
