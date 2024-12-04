#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time

hdwallet = HDWallet(symbol=BTC)

infile = open('wifs.txt','r')
good = open('wifs-good.txt','w')
bad = open('wifs-bad.txt','w')

def go(k):
	try:
		hdwallet.from_wif(wif=k)
	except:
		bad.write(k+'\n')
		bad.flush()
		return
	good.write(k+'\n')
	good.flush()

print('Reading...')
lines = infile.read().splitlines()

print('Writing...')
for line in tqdm(lines):
	go(line)

print('\a', end='', file=sys.stderr)