#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

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

print('Reading...', flush=True)
lines = infile.read().splitlines()

print('Writing...', flush=True)
for line in tqdm(lines):
	go(line)

print('\a', end='', file=sys.stderr)
