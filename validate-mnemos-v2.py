#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time

hdwallet = HDWallet(symbol=BTC)

infile = open('mnemos.txt','r')
good = open('mnemos-good.txt','w')
bad = open('mnemos-bad.txt','w')

def go(k):
	try:
		hdwallet.from_mnemonic(mnemonic=k)
	except:
		bad.write(k+'\n')
		bad.flush()
		return
	good.write(hdwallet.mnemonic()+'\n')
	good.flush()

print('Reading...')
lines = infile.read().splitlines()
lines = [x.strip() for x in lines]

print('Writing...')
process_map(go, lines, max_workers=6, chunksize=1000, ascii=False)

print('\a', end='', file=sys.stderr)
