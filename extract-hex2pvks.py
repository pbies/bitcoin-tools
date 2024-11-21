#!/usr/bin/env python3

import os, sys, re
from pathlib import Path

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

files = Path('.').glob('*.out')
o = open('output.txt','w')

for f in files:
	wallet_path = str(f)
	print(wallet_path+'...')
	i=open(wallet_path,'r').read().splitlines()
	a=[]
	for j in i:
		a.extend(find_all_matches('[0-9a-fA-F]{64}',j))
	if a!=[]:
		for i in a:
			o.write(i+'\n')
	o.flush()

print('\a', end='', file=sys.stderr)