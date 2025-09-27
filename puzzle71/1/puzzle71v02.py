#!/usr/bin/env python3

import datetime
import os
import random
import sys
import time
from multiprocessing import Pool
import secp256k1 as ice
from tqdm import tqdm

RANGE_START = 0x400000000000000000
RANGE_END   = 0x7fffffffffffffffff
SIZE = RANGE_END - RANGE_START
RANGE_SIZE = 2**24
R = range(RANGE_START, RANGE_END+1)
TARGET = 'f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8'
th = 24
cnt = int(RANGE_SIZE/50)
LOG_FILE = 'log.txt'

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	formatted = f"{timestamp} {message}"
	print(formatted, flush=True, end='')
	with open(LOG_FILE, 'a') as logfile:
		logfile.write(formatted)

def go(pvk):
	h = ice.privatekey_to_h160(0, True, pvk).hex()
	if h == TARGET:
		log(f'Found: {hex(pvk)[2:].zfill(64)}\n')
		print('\a', end='', file=sys.stderr)
		sys.exit(0)

def main():
	os.system('cls' if os.name == 'nt' else 'clear')

	tmp=0
	#random.seed(0)

	while True:
		try:
			start_range = random.randint(RANGE_START, RANGE_END - RANGE_SIZE)
			end_range = start_range + RANGE_SIZE
			print(f"{hex(start_range)[2:]}:{hex(end_range)[2:]}")
			with Pool(processes=th) as p, tqdm(total=RANGE_SIZE) as pbar:
				for result in p.imap_unordered(go, range(start_range, end_range), chunksize=1000):
					if tmp%cnt==0:
						pbar.update(cnt)
						pbar.refresh()
					tmp=tmp+1

		except KeyboardInterrupt:
			print("\n\nScanning stopped by user.")
			sys.exit(0)

if __name__ == "__main__":
	main()
