#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import sys
import psutil
import time
import math

cpu=psutil.cpu_count()
x=50000

def go(k):
	j=0
	for i in range(0,20000):
		j=j+1
	return j

st = time.time()

times=[]
i=0
for th in range(2,cpu+1,2):
	print(f'{th} threads:')
	start=time.time()
	with Pool(processes=th) as p, tqdm(total=x) as pbar:
		for result in p.imap_unordered(go, range(0,x), chunksize=1000):
			if i%1000==0:
				pbar.update(1000)
				pbar.refresh()
			i=i+1
	took=time.time()-start
	print(f'time: {took:.3f} s')
	times.append([th,took])

et = time.time()

low_time=1000
low_th=0

for th, ti in times:
	if low_time>ti:
		low_time=ti
		low_th=th

diff = et-st

print(f'Fastest: {low_th} threads = {low_time:.3f} s\a')
print(f'Time: {math.floor(diff/60)}m{diff%60:.3f}s')
