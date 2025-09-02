#!/usr/bin/env python3

import sys, os, datetime, time, hashlib, base58
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from ecdsa import SigningKey, SECP256k1

def ripemd160(b: bytes) -> bytes:
	return hashlib.new("ripemd160", b).digest()

def sha256(b: bytes) -> bytes:
	return hashlib.sha256(b).digest()

def hash160(data: bytes) -> bytes:
	return ripemd160(sha256(data))

def pubkey_to_addr(pubkey_hex: str) -> str:
	pubkey_bytes = bytes.fromhex(pubkey_hex)
	vh160 = b"\x00" + hash160(pubkey_bytes)
	checksum = sha256(sha256(vh160))[:4]
	return base58.b58encode(vh160 + checksum).decode()

def pvk_to_pubkey(key: bytes | str) -> str:
	key_bytes = bytes.fromhex(key) if isinstance(key, str) else key
	sk = SigningKey.from_string(key_bytes, curve=SECP256k1)
	return (b"\x04" + sk.verifying_key.to_string()).hex()

def pvk_to_addr(pvk: bytes | str) -> str:
	return pubkey_to_addr(pvk_to_pubkey(pvk))

def log(message: str):
	ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open("log.txt", "a") as f:
		f.write(f"{ts} {message}\n")
	print(f"{ts} {message}", flush=True)

# Global set 'addrs' will be provided to worker processes via initializer
addrs = None

def _init_pool(_addrs):
	global addrs
	addrs = _addrs

def go(x):
	global addrs
	pvk = hex(x)[2:].zfill(64)
	a = pvk_to_addr(pvk)
	if a in addrs:
		log(f"{pvk} {a}")

def main():
	global addrs
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time = time.time()

	print('Reading...')
	with open('addrs-with-bal.txt','r') as f:
		addrs_local = set(f.read().splitlines())

	r = range(1, (2**32) + 1)
	total_items = len(r)
	print('Searching...')

	# Determine worker count (keep your previous 28 default, but cap to CPU count if smaller)
	workers = 28 if 28 > 0 else cpu_count()

	with Pool(processes=workers, initializer=_init_pool, initargs=(addrs_local,)) as pool:
		# tqdm progress bar over imap_unordered for better throughput
		for _ in tqdm(pool.imap_unordered(go, r, chunksize=100), total=total_items, smoothing=0.1, miniters=1):
			pass

	stop_time = time.time()
	print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {stop_time-start_time:.3f} seconds')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
