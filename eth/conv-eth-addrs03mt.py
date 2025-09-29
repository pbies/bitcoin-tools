#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, os, datetime, time

def go(j):
	w=f'{j}\n{j[2:]}\n{j.lower()}\n{j[2:].lower()}\n'
	with open('output.txt','a') as o:
		o.write(w)

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	i=open('input.txt','r').read().splitlines()

	c=1000
	t=0
	with Pool(processes=24) as p, tqdm(total=len(i)) as pbar:
		for result in p.imap_unordered(go, i, chunksize=1000):
			t=t+1
			if t==c:
				pbar.update(c)
				pbar.refresh()
				t=0

	stop_time=time.time()
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {stop_time-start_time:.3f} seconds')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
