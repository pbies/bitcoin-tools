#!/usr/bin/env python3

import sys
from tqdm import tqdm

for j in sys.stdin:
	j=j.rstrip()
	for i in range(len(j),-2,-2):
		print(j[i:i+2],end='')
	print()

print('\a', end='', file=sys.stderr)
