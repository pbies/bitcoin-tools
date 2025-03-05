#!/usr/bin/env python3

import os, sys, re
from pathlib import Path
from tqdm import tqdm

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

i = open('input.txt','r').read().splitlines()
o = open('output.txt','w')

for l in tqdm(i):
	a=[]
	a.extend(find_all_matches('[0-9a-fA-F]{64}', l))
	if a!=[]:
		for i in a:
			o.write(i+'\n')
	o.flush()

print('\a', end='', file=sys.stderr)
