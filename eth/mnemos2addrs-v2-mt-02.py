#!/usr/bin/env python3

# pip install bip-utils

from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import json, os, sys
from tqdm import tqdm
from multiprocessing import Pool

infile = open('input.txt','rb')
i=infile.tell()
tmp = 0
cnt = 10000

def go(x):
	x=x.rstrip(b'\n').decode()

	for i in range(0, 4):
		for j in range(0, 4):
			address = get_ethereum_address(x, i, j)
			if address is not None:
				outfile.write(f'{address} {x}:{i}/{j}\n')

	outfile.flush()

def get_ethereum_address(mnemonic, index=0, account=0):
	try:
		seed = Bip39SeedGenerator(mnemonic).Generate()
		bip44_mst = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
		account = bip44_mst.Purpose().Coin().Account(account).Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
		return account.PublicKey().ToAddress()
	except:
		return None

outfile = open('output.txt','w')

size = os.path.getsize('input.txt')
th=24

if __name__=='__main__':
	os.system('cls||clear')
	pbar=tqdm(total=size)
	with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			i=infile.tell()
			r=i-tmp
			if r>cnt:
				tmp=i
				pbar.update(r)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)
