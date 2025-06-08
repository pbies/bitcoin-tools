#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
import base58
import os
import sys

def go(x):
	a=0
	for i in range(0,1000):
		a=a+1

if __name__ == '__main__':
	r=range(1,int(1e6)+1)
	process_map(go, r, max_workers=16, chunksize=1000)

	print('\a', end='', file=sys.stderr)
