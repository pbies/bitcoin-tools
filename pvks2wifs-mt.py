#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from urllib.request import urlopen
import json
import sys
import time

hdwallet = HDWallet(symbol=BTC)

def go(k):
	try:
		hdwallet.from_private_key(private_key=k)
	except:
		return
	outfile.write(hdwallet.wif()+' 0\n')
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.read().splitlines()

process_map(go, lines, max_workers=12, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
