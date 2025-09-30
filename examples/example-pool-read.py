#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, os

infile = open('input.txt','rb')
size = os.path.getsize('input.txt')

def go(x):
	y=x.rstrip(b'\n').decode()
	o=f'{y}\n'
	with open('output.txt','a') as outfile:
		outfile.write(o)

def main():
	th=24
	cnt=int(1e5)
	tmp=0

	open('output.txt', 'w').close()

	with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			pos=infile.tell()
			r=pos-tmp
			if r>cnt:
				tmp=pos
				pbar.update(r)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
