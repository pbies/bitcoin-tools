#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
import pprint
import random
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

def go(k):
	hdwallet.from_private_key(private_key=k)
	d=hdwallet.dumps()['addresses']
	outfile.write(hdwallet.dumps()['wif']+'\n'+d['p2pkh']+'\n'+d['p2sh']+'\n'+d['p2wpkh']+'\n'+d['p2wpkh_in_p2sh']+'\n'+d['p2wsh']+'\n'+d['p2wsh_in_p2sh']+'\n')

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=12, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
