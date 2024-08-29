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
		hdwallet.from_private_key(private_key=k)
	except:
		return
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

infile = open('pvks.txt','r')
outfile = open('pvks-output.txt','w')
print('Reading 1...', flush=True)
lines = infile.read().splitlines()

g=[]

print('Reading 2...', flush=True)
for i in tqdm(lines):
	for j in range(-5,6):
		t=hex(int(i,16)+j)[2:]
		t='0'*(64-len(t))+t
		g.append(t)

print('Writing...', flush=True)
process_map(go, g, max_workers=12, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
