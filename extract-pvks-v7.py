#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, os, re

infile = open('input.txt','rb')

size = os.path.getsize('input.txt')
tmp = 0
cnt = 1e6
th=24
i=0

outfile = open('output.txt','w')

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

def go(line):
	x=find_all_matches('[0-9a-fA-F]{64}', line.decode())
	return x

with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
	for result in p.imap_unordered(go, infile, chunksize=1000):
		for i in result:
			outfile.write(f'{i}\n')
		pos=infile.tell()
		r=pos-tmp
		if r>cnt:
			tmp=pos
			outfile.flush()
			pbar.update(r)
			pbar.refresh()

print('\a', end='', file=sys.stderr)
