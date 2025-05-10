#!/usr/bin/env python3

import re
import sys
from tqdm import tqdm

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

print('Reading...', flush=True)
f=open('input.txt', 'r').read()
a=[]
print('Searching...', flush=True)
a.extend(find_all_matches('[0-9a-fA-F]{64}', f))
o=open('output.txt', 'w')

print('Writing...', flush=True)
for i in tqdm(a):
	o.write(f'{i}\n')
	o.flush()

print('\a', end='', file=sys.stderr)
