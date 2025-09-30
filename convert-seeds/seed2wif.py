#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

def go(k):
	try:
		hdwallet.from_seed(seed=k)
	except:
		return
	outfile.write(hdwallet.wif()+'\n')
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=4, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
