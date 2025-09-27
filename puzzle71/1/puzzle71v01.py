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
R = range(RANGE_START, RANGE_END+1)
TARGET = 'f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8'
th = 24
cnt = 200000
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

	try:
		with Pool(processes=th) as p, tqdm(total=SIZE) as pbar:
			for result in p.imap_unordered(go, R, chunksize=1000):
				if tmp%cnt==0:
					pbar.update(cnt)
					pbar.refresh()
				tmp=tmp+1

		print('\a', end='', file=sys.stderr)
	except KeyboardInterrupt:
		print("\n\nScanning stopped by user.")

if __name__ == "__main__":
	main()
