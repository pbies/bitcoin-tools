#!/usr/bin/env python3

import datetime
import os
import random
import sys
import time
from multiprocessing import Pool
import secp256k1 as ice

# Configs
RANGE_START = 0x80000000000000000
RANGE_END   = 0xfffffffffffffffff
RANGE_SIZE  = 1048576
TARGET_HASH = bytes.fromhex('e0b8a2baee1b77fc703455f39d51477451fc8cfc')
NUM_PROCESSES = 24
PROGRESS_COUNT = 1000000
CHUNK_SIZE = 1024

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	formatted = f"{timestamp} {message}"
	print(formatted, flush=True, end='')
	with open('log.txt', 'a') as logfile:
		logfile.write(formatted)
		logfile.flush()

def check_key(pvk):
	h = ice.privatekey_to_h160(0, True, pvk)
	if h == TARGET_HASH:
		message = f"Found pvk: {hex(pvk)[2:]}  |  WIF: {ice.btc_pvk_to_wif(pvk, False)}\a\n"
		print()
		log(message)
		print('\a', end='', file=sys.stderr)
	return 1

def main():
	os.system('cls||clear')
	print("Puzzle 68 random scanner")
	print("Scanning random addresses in an infinite loop. Press Ctrl+C to stop.\n")

	keys_checked = 0
	start_time = time.time()

	try:
		with Pool(processes=NUM_PROCESSES) as pool:
			while True:
				start_range = random.randint(RANGE_START, RANGE_END - RANGE_SIZE)
				end_range = start_range + RANGE_SIZE
				current_range_str = f"{hex(start_range)[2:]}:{hex(end_range)[2:]}"
				ela = str(datetime.timedelta(seconds=round(time.time()-start_time)))

				for _ in pool.imap_unordered(check_key, range(start_range, end_range), chunksize=CHUNK_SIZE):
					keys_checked += 1
					if keys_checked % PROGRESS_COUNT == 0:
						elapsed = time.time() - start_time
						rate = keys_checked / elapsed if elapsed > 0 else 0
						print(f"\rKeys checked: {keys_checked:,} | Rate: {rate:,.0f} keys/sec | Range: {current_range_str} | Elapsed: {ela}", end="", flush=True)
	except KeyboardInterrupt:
		print("\n\nScanning stopped by user.")
		print(f"Total keys checked: {keys_checked:,}")

if __name__ == "__main__":
	main()
