#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import sys
import psutil

cpu=psutil.cpu_count()
x=10000

def go(k):
	j=0
	for i in range(0,k):
		j=j+1
	return j

i=0
for th in range(2,cpu+1,2):
	print(f'{th} threads:')
	with Pool(processes=th) as p, tqdm(total=x) as pbar:
		for result in p.imap_unordered(go, range(0,x), chunksize=1000):
			if i%1000==0:
				pbar.update(1000)
				pbar.refresh()
			i=i+1

print('\a', end='', file=sys.stderr)
