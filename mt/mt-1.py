#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed

def go():
	print('.',end='',flush=True)

ex=ThreadPoolExecutor(max_workers=4)
while True:
	ex.submit(go)
