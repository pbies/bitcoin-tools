#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
import base58
import hashlib
import os
import sys
import time

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

infile = open('input.txt','rb')
i=infile.tell()
tmp = 0
cnt = 100000

def go(x):
	global tmp, i
	x=x.rstrip(b'\n')
	sha1=hashlib.sha256(x).hexdigest()
	shatmp=hashlib.sha256(x).digest()
	sha2=hashlib.sha256(shatmp).hexdigest()
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=sha1)
		hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=sha2)
	except:
		return
	pvk1=hdwallet1.private_key()
	pvk2=hdwallet2.private_key()
	wif1=pvk_to_wif2(pvk1)
	wif2=pvk_to_wif2(pvk2)
	w=f'{wif1}\n{hdwallet1.wif()}\n{hdwallet1.address("P2PKH")}\n{hdwallet1.address("P2SH")}\n{hdwallet1.address("P2TR")}\n{hdwallet1.address("P2WPKH")}\n{hdwallet1.address("P2WPKH-In-P2SH")}\n{hdwallet1.address("P2WSH")}\n{hdwallet1.address("P2WSH-In-P2SH")}\n\n'
	w+=f'{wif2}\n{hdwallet2.wif()}\n{hdwallet2.address("P2PKH")}\n{hdwallet2.address("P2SH")}\n{hdwallet2.address("P2TR")}\n{hdwallet2.address("P2WPKH")}\n{hdwallet2.address("P2WPKH-In-P2SH")}\n{hdwallet2.address("P2WSH")}\n{hdwallet2.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(w)
	outfile.flush()

outfile = open('output.txt','w')

size = os.path.getsize('input.txt')
th=24
CHUNK_SIZE=1024
PROGRESS_COUNT = 1000

if __name__=='__main__':
	os.system('cls||clear')
	keys_checked = 0
	start_time = time.time()
	with Pool(processes=th) as pool:
		for result in pool.imap_unordered(go, infile, chunksize=CHUNK_SIZE):
			keys_checked += 1
			if keys_checked % PROGRESS_COUNT == 0:
				elapsed = time.time() - start_time
				rate = keys_checked / elapsed if elapsed > 0 else 0
				print(f"\rConverted: {keys_checked:,} | Rate: {rate:.2f} keys/sec", end="", flush=True)
	print('\nDone!')

	print('\a', end='', file=sys.stderr)
