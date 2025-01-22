#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time

hdwallet = HDWallet(symbol=BTC)

def go(k):
	try:
		hdwallet.from_mnemonic(mnemonic=k)
	except:
		return
	outfile.write(hdwallet.mnemonic()+'\n')
	outfile.flush()

infile = open('mnemos.txt','r')
outfile = open('mnemos-out.txt','a')

print('Reading...', flush=True)
lines = infile.read().splitlines()
lines = [x.strip() for x in lines]

print('Writing...', flush=True)
process_map(go, lines, max_workers=6, chunksize=1000, ascii=False)

print('\a',end='',file=sys.stderr)
