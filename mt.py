#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed

def go():
	print('.',end='',flush=True)

ex=ThreadPoolExecutor(max_workers=4)
while True:
	ex.submit(go)

###

from multiprocessing import Pool
import tqdm
import time

def _foo(my_number):
	square = my_number * my_number
	time.sleep(1)
	return square 

if __name__ == '__main__':
	with Pool(2) as p:
		r = list(tqdm.tqdm(p.imap(_foo, range(30)), total=30))

###

from tqdm.contrib.concurrent import process_map  # or thread_map
import time

def _foo(my_number):
	square = my_number * my_number
	time.sleep(1)
	return square 

if __name__ == '__main__':
	r = process_map(_foo, range(0, 30), max_workers=2)

###

#!/usr/bin/env python3

from multiprocessing.pool import Pool

def go(arg):
	print(arg, end=' ')

pool = Pool(4)

pool.map(go, range(16384), chunksize=4096)

pool.close()
pool.join()
