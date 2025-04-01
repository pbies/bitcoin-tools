#!/usr/bin/env python3

import os, sys
from multiprocessing import Pool
from tqdm import tqdm

o=open('output.txt','w')

count=1000000
th=4
cnt=10000

def go(x):
	o.write(f'{os.urandom(32).hex()}\n')
	o.flush

c=0
with Pool(processes=th) as p, tqdm(total=count) as pbar:
	for result in p.imap(go, range(0,count)):
		if c%cnt==0:
			pbar.update(cnt)
			pbar.refresh()
		c=c+1

print('\a', end='', file=sys.stderr)
