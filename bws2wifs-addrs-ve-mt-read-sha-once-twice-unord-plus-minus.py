#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
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
cnt = 10000

def go(x):
	global tmp, i
	x=x.rstrip(b'\n')
	sha1=hashlib.sha256(x).hexdigest()
	shatmp=hashlib.sha256(x).digest()
	sha2=hashlib.sha256(shatmp).hexdigest()
	n=int(sha1, 16)
	o=int(sha2, 16)
	for m in range(-3, 4):
		g=hex(n+m)[2:].zfill(64)
		h=hex(o+m)[2:].zfill(64)
		try:
			hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=g)
			hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=h)
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
	with Pool(processes=th) as pool, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in pool.imap_unordered(go, infile, chunksize=CHUNK_SIZE):
			i=infile.tell()
			r=i-tmp
			if r>cnt:
				tmp=i
				pbar.update(r)
				pbar.refresh()
	print('\nDone!\a')
