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

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(x):
	x=x.rstrip(b'\n')
	y=base58.b58decode_check(x).hex()
	w=f'{y}\n'
	with open('output.txt','a') as outfile:
		outfile.write(w)

def main():
	print('Reading...', flush=True)
	infile = open('input.txt','rb').read().splitlines()
	i=len(infile)
	tmp = 0
	cnt = 1000
	th=24
	print('Writing...', flush=True)
	with Pool(processes=th) as p, tqdm(total=i) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			if tmp%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			tmp=tmp+1

	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
