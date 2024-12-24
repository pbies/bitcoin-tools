#!/usr/bin/env python3

from tqdm import tqdm
import sys

for j in sys.stdin:
	j=j.rstrip()
	for i in range(len(j),-2,-2):
		print(j[i:i+2],end='')
	print()

print('\a', end='', file=sys.stderr)
