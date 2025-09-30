#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map

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

infile = open('hex.txt','r')
outfile = open('hex-output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=4, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
