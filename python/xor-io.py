#!/usr/bin/env python3

import sys
from tqdm import tqdm

x=2**256-1

for j in sys.stdin:
	a=int(j.rstrip(),16)
	b=a^x
	c=hex(b)[2:].zfill(64)
	print(c)

print('\a', end='', file=sys.stderr)
