#!/usr/bin/env python3

from multiprocessing import Pool
import datetime
import ecdsa
import hashlib
import os
import random
import sys
import time
import secp256k1 as ice

def log(t):
	d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print(f'{d} {t}', flush=True, end='')
	l=open('log.txt','a')
	l.write(f'{d} {str(t)}')
	l.flush()
	l.close()

def go(pvk):
	h=ice.privatekey_to_h160(0, True, pvk) # type = 0 [p2pkh],  1 [p2sh],  2 [bech32] ; compressed?
	if h==target_hash:
		print()
		log(f'Found pvk: {hex(pvk)[2:]}  |  WIF: {ice.btc_pvk_to_wif(pvk, False)}\a\n')
		print('\a', end='', file=sys.stderr)

range_start = 0x80000000000000000
range_end   = 0xfffffffffffffffff
r           = 262144
target_hash = bytes.fromhex('e0b8a2baee1b77fc703455f39d51477451fc8cfc')
th = 24
cnt=10000
# seed=0

def main():
	try:
		os.system('cls||clear')
		print("Puzzle 68 random scanner")
		print("Scanning random addresses in an infinite loop. Press Ctrl+C to stop.\n")

		keys_checked = 0
		start_time = time.time()
		# random.seed(seed)

		while True:
			rnd = random.randint(range_start, range_end+1)

			rng = range(rnd, rnd+r)

			with Pool(processes=th) as p:
				for result in p.imap(go, rng):
					keys_checked += 1
					if keys_checked % cnt == 0:
						elapsed = time.time() - start_time
						rate = keys_checked / elapsed
						print(f"\rKeys checked: {keys_checked:,} | Rate: {rate:.2f} keys/sec | Range: {hex(rnd)[2:]}-{hex(rnd+r)[2:]}", end="", flush=True)

	except KeyboardInterrupt:
		print("\n\nScanning stopped by user.")
		print(f"Total keys checked: {keys_checked:,}")

if __name__ == "__main__":
	main()
