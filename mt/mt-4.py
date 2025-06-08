#!/usr/bin/env python3

from multiprocessing.pool import Pool

def go(arg):
	print(arg, end=' ')

pool = Pool(4)

pool.map(go, range(16384), chunksize=4096)

pool.close()
pool.join()
