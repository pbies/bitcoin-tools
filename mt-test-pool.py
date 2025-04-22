#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import os
import sys

def go(x):
	a=0
	for i in range(0,1000):
		a=a+1

th=16
max_=int(1e6)+1

if __name__ == '__main__':
	r=range(1,max_)
	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, r, chunksize=1000):
			if i%1000==0:
				pbar.update(1000)
				pbar.refresh()
			i=i+1

	print('\a', end='', file=sys.stderr)

