#!/usr/bin/env python3

from multiprocessing import Pool
import time
from tqdm import *

def _foo(my_number):
	square = my_number * my_number
	time.sleep(1)
	return square 

if __name__ == '__main__':
	with Pool(processes=2) as p:
		max_ = 30
		with tqdm(total=max_) as pbar:
		for _ in p.imap_unordered(_foo, range(0, max_), chunksize=1000):
			pbar.update()
