#!/usr/bin/env python3

# this script is slowest

from ecdsa import SigningKey, SECP256k1
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from threading import Thread, Lock
from queue import Queue
from tqdm import tqdm
import base58, re
import os, sys, hashlib

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
order = SECP256k1.order

# Thread-safe lock for file writing
output_lock = Lock()

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	if entropy_int >= order or entropy_int < 1:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()

def worker(queue, pbar):
	while True:
		try:
			k = queue.get(timeout=1)
		except:
			break
			
		p = entropy_to_pvk(k)
		if p is None:
			queue.task_done()
			pbar.update(1)
			continue
			
		try:
			w = pvk_to_wif2(p)
			hdwallet.from_private_key(p)
		except:
			queue.task_done()
			pbar.update(1)
			continue
			
		r = f'{w}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
		
		with output_lock:
			with open('output.txt', 'a') as o:
				o.write(r)
		
		queue.task_done()
		pbar.update(1)

print('Reading...', flush=True)
lines = set(open('input.txt','r').read().splitlines())

print('Writing...', flush=True)
open('output.txt', 'w').close()

# Create queue and add all lines
queue = Queue()
for line in lines:
	queue.put(line)

# Number of threads (equivalent to your previous 24 processes)
num_threads = 24

# Create progress bar
pbar = tqdm(total=len(lines))

# Create and start threads
threads = []
for _ in range(num_threads):
	thread = Thread(target=worker, args=(queue, pbar))
	thread.daemon = True
	thread.start()
	threads.append(thread)

# Wait for all tasks to complete
queue.join()

# Wait for all threads to finish
for thread in threads:
	thread.join()

pbar.close()

print('\a', end='', file=sys.stderr)
