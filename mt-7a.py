#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
import sys

max_ = int(1e5)
th = 8

def go(i):
	pass

i=1

if __name__ == "__main__":
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, range(0, max_), chunksize=1000):
			if i%2000==0:
				pbar.update(2000)
				pbar.refresh()
			i=i+1

	print('\a', end='', file=sys.stderr)
