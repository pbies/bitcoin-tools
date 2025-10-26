#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import sys, base58, os
from tqdm.contrib.concurrent import process_map

outfile_path = 'output.txt'

def gen():
	for i in tqdm(range(1, 255)):
		for j in range(1, 257):
			for k in range(-1024, 1025):
				n=hex(abs((i<<j)+k))[2:].zfill(64)
				yield n

def go(x):
	with open(outfile_path, 'a') as outfile:
		outfile.write(f'{x}\n')

def main():
	process_map(go, gen(), max_workers=24, chunksize=1000)
	#with Pool(processes=24) as p:
	#	p.imap_unordered(go, gen(), chunksize=10000)
	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
