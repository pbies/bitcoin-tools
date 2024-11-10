#!/usr/bin/env python3

from web3.auto import w3
from tqdm.contrib.concurrent import process_map

infile=open('input.txt','r')
outfile=open('output.txt','w')

def go(i):
	i=i.strip()
	w3.eth.account.enable_unaudited_hdwallet_features()
	try:
		acc = w3.eth.account.from_mnemonic(i)
	except:
		return
	outfile.write(acc.address+' '+acc._private_key.hex()+'\n')
	outfile.flush()

process_map(go, infile, max_workers=10, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
