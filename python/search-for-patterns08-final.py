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
outfile = open(sys.argv[3], 'w')

size = os.path.getsize(sys.argv[2])
pbar = tqdm(total=size, unit='B', unit_scale=True)

c = 0   # blocks processed
r = 0   # total found
z = 0   # unique found
t = 0   # position tracker

while True:
	# read up to 10 lines, stop only on real EOF
	lines = []
	for _ in range(12):
		line = infile.readline()
		if not line:  # real EOF
			break
		lines.append(line.rstrip('\n'))

	if not lines:  # nothing read -> EOF
		break

	# check all lines in the batch
	found = [x for x in lines if x in patt]
	if found:
		patt.difference_update(found)
		z += len(found)
		r += 1
		outfile.write('\n'.join(lines) + '\n')
		outfile.flush()

		# live status update (unchanged)
		sys.stdout.write('\0337')
		sys.stdout.write('\033[1;1H')
		sys.stdout.write('\033[2K\r')
		sys.stdout.write(f'### Found: {r} ; Unique: {z} ###\n')
		sys.stdout.write('\033[2K')
		sys.stdout.write('\0338')
		sys.stdout.flush()

		if not patt:
			print(f'Found: {r} ; Unique: {z}')
			print('\a', end='', file=sys.stderr)
			sys.exit(0)

	# progress update per batch using file position
	i = infile.tell()
	q = i - t
	t = i
	if q > 0:
		pbar.update(q)
		pbar.refresh()

print(f'Found: {r} ; Unique: {z}')
print('\a', end='', file=sys.stderr)
