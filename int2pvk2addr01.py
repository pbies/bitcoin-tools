#!/usr/bin/env python3

import sys, os, datetime, time
from tqdm.contrib.concurrent import process_map

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

def go(x):
	global addrs
	pvk=hex(x)[2:].zfill(64)
	a=pvk_to_addr(pvk)
	if a in addrs:
		log(f'{a}\n')

def main():
	global addrs
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	print('Reading...')
	addrs=set(open('addrs-with-bal.txt','r').read().splitlines())
	r=range(1, (2**32)+1)
	print('Searching...')
	process_map(go, r, max_workers=28, chunksize=100)

	stop_time=time.time()
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {stop_time-start_time:.3f} seconds')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
