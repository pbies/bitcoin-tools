#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from urllib.request import urlopen
from tqdm import tqdm
import json
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

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=4, chunksize=1000, ascii=False)

import sys
print('\a',end='',file=sys.stderr)
