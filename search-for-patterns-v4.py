#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
import hashlib, base58
import sys

if len(sys.argv)<4:
	print(f'Usage: {sys.argv[0]} patterns_file search_in_file output_file')
	sys.exit(1)

patt=set(open(sys.argv[1],'r').read().splitlines())
cnt=len(patt)
print(f'Searching for {cnt} patterns...')

with open(sys.argv[2], 'r') as infile, open(sys.argv[3], 'w') as outfile:
	lines = infile.readlines()

	c=0
	r=0

	for i in range(0, len(lines), 10):  # Process 10 lines at a time
		tmp = [line.rstrip() for line in lines[i:i+9]]

		if any(x in patt for x in tmp):
			patt.difference_update(tmp)  # Remove found patterns
			outfile.write('\n'.join(tmp) + '\n\n')
			outfile.flush()
			r += 1

		c += 1
		if c % 10_000 == 0:
			print(f'Found: {r} ; Progress: {c}', end='\r')

print(f'Found: {r} ; Progress: {c}')

print('\a', end='', file=sys.stderr)
