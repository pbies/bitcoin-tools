#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map # or thread_map
import time

def _foo(my_number):
	square = my_number * my_number
	time.sleep(1)
	return square 

if __name__ == '__main__':
	r = process_map(_foo, range(0, 30), max_workers=2) # chunksize=?
