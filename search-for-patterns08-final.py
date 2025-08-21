#!/usr/bin/env python3

import sys, os
from tqdm import tqdm

if len(sys.argv) < 4:
	print(f'Usage: {sys.argv[0]} patterns_file search_in_file output_file')
	sys.exit(1)

# Load patterns as set for O(1) lookups
patt = set(open(sys.argv[1], 'r').read().splitlines())
cnt = len(patt)
print(f'Searching for {cnt} patterns...')

infile = open(sys.argv[2], 'r')
outfile = open(sys.argv[3], 'a')

size = os.path.getsize(sys.argv[2])
pbar = tqdm(total=size, unit='B', unit_scale=True)

c = 0   # blocks processed
r = 0   # total found
z = 0   # unique found
t = 0   # position tracker

while True:
	lines = [infile.readline().rstrip() for _ in range(10)]
	if not lines[0]:  # EOF
		break

	tmp = lines[:9]  # use first 9 lines (as in v4)
	found = [x for x in tmp if x in patt]

	if found:
		patt.difference_update(tmp)
		z += len(found)
		r += 1
		outfile.write('\n'.join(tmp) + '\n\n')
		outfile.flush()

		# live status update
		sys.stdout.write('\0337')
		sys.stdout.write('\033[1;1H')
		sys.stdout.write('\033[2K\r')
		sys.stdout.write(f'### Found: {r} ; Unique: {z} ###\n')
		sys.stdout.write('\033[2K')
		sys.stdout.write('\0338')
		sys.stdout.flush()

		if not patt:  # all found
			print(f'Found: {r} ; Unique: {z}')
			print('\a', end='', file=sys.stderr)
			sys.exit(0)

	c += 1
	if c % 1000 == 0:  # update progress every 1000 blocks
		i = infile.tell()
		q = i - t
		t = i
		pbar.update(q)
		pbar.refresh()

print(f'Found: {r} ; Unique: {z}')
print('\a', end='', file=sys.stderr)
