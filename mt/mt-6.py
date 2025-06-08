#!/usr/bin/env python3

from p_tqdm import p_map
import time

def _foo(my_number):
	square = my_number * my_number
	time.sleep(1)
	return square 

if __name__ == '__main__':
	r = p_map(_foo, list(range(0, 30)))
