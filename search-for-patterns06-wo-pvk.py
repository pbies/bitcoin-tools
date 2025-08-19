#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
import hashlib, base58
import sys, os
from tqdm import tqdm

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
z=set()

size=os.path.getsize(sys.argv[2])
t=0
pbar=tqdm(total=size, unit='B', unit_scale=True)

while True:
	#pvk=infile.readline().rstrip()
	#if not pvk:
	#	break
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
	adr7=infile.readline().rstrip()
	empty=infile.readline().rstrip()

	tmp=[wif1,wif2,adr1,adr2,adr3,adr4,adr5,adr6,adr7]

	for x in patt:
		if x in tmp:
			patt.remove(x)
			z.add('\n'.join(tmp)+'\n\n')
			sys.stdout.write('\0337')
			sys.stdout.write('\033[1;1H')
			sys.stdout.write('\033[2K')   # Clear entire line
			sys.stdout.write('\r')        # Move cursor to the beginning of the line
			sys.stdout.write(f'### Found: {r} ; Unique: {len(z)} ###   \n')
			sys.stdout.write('\033[2K')   # Clear entire line
			sys.stdout.write('\0338')
			sys.stdout.flush()
			r=r+1
			if r==cnt:
				outfile.writelines(z)
				outfile.flush()

				print(f'Found: {r} ; Unique: {len(z)}')

				print('\a', end='', file=sys.stderr)
				sys.exit(0)

	c=c+1
	if c%1_000==0:
		i=infile.tell()
		q=i-t
		t=i
		pbar.update(q)
		pbar.refresh()
		#print(f'Found: {r} ; Progress: {c}', end='\r')

outfile.writelines(z)
outfile.flush()

print(f'Found: {r} ; Unique: {len(z)}')

print('\a', end='', file=sys.stderr)
