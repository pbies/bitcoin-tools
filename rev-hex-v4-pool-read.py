#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, os

infile = open('input.txt','rb')

size = os.path.getsize('input.txt')
tmp = 0
cnt = 100000
th=24
i=0

outfile = open('output.txt','w')

def go(line):
	line=line[:-1].decode()
	h1=line[::-1]
	try:
		h2=bytes.fromhex(line)
	except:
		return
	h2=h2[::-1]
	h2=h2.hex()
	outfile.write(f'{line}\n{h1}\n{h2}\n')
	outfile.flush()

with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
	for result in p.imap(go, infile):
		pos=infile.tell()
		r=pos-tmp
		if r>cnt:
			tmp=pos
			pbar.update(r)
			pbar.refresh()

print('\a', end='', file=sys.stderr)
