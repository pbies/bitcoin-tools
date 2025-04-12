#!/usr/bin/env python3

import datetime
import os
import random
import sys
import time
from multiprocessing import Pool
import psutil
import hashlib

# Configs
PROGRESS_COUNT = 10000
CHUNK_SIZE = 1024
LOG_FILE = 'log.txt'
CPU_THREADS=psutil.cpu_count()
CHECK_MAX=500_000

def sha(x):
	return hashlib.sha256(x).digest()

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	formatted = f"{timestamp} {message}"
	print(formatted, flush=True, end='')
	with open(LOG_FILE, 'a') as logfile:
		logfile.write(formatted)
		logfile.flush()

def go(data):
	s=sha(data)
	#print(s)

def data_gen():
	for _ in range(CHECK_MAX):
		yield os.urandom(1024)

def main():
	os.system('cls||clear')

	max_rate=0
	max_rate_th=0

	for i in range(2, CPU_THREADS+1, 2):
		checked = 0
		try:
			with Pool(processes=i) as pool:
				start_time = time.time()
				#print(f'Using {i} CPU thread(s)')
				#while True:
				for _ in pool.imap_unordered(go, data_gen(), chunksize=CHUNK_SIZE):
					ela = str(datetime.timedelta(seconds=time.time()-start_time))
					checked += 1
					if checked % PROGRESS_COUNT == 0:
						elapsed = time.time() - start_time
						rate = checked / elapsed if elapsed > 0 else 0
						print(f"\rUsing {i} CPU thread(s) | Checked: {checked:,} | Rate: {rate:,.0f}/sec | Elapsed: {ela}", end="", flush=True)
					if checked >= CHECK_MAX:
						elapsed = time.time() - start_time
						rate = checked / elapsed if elapsed > 0 else 0
						if rate>max_rate:
							max_rate=rate
							max_rate_th=i
						#pool.terminate()
						print()
						break
				pool.close()
				pool.join()
		except KeyboardInterrupt:
			print("\n\nScanning stopped by user.")
			exit(0)
	print(f'Max rate: {max_rate} with {max_rate_th} threads')

if __name__ == "__main__":
	main()
