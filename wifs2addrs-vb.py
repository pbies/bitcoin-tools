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

infile = open('input.txt','rb')
i=infile.tell()
tmp = 0
cnt = 10000

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def go(x):
	x=x.rstrip(b'\n').decode()
	try:
		hdwallet.from_wif(wif=x)
	except:
		return
	w=f'{x}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(w)
	outfile.flush()

outfile = open('output.txt','w')

size = os.path.getsize('input.txt')
th=10
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
