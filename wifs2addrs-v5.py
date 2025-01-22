#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import base58
import sys

hdwallet = HDWallet(symbol=BTC)

def go(k):
	try:
		hdwallet.from_wif(wif=k)
	except:
		return
	outfile.write(k+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

print('Reading...', flush=True)
infile = open(sys.argv[1],'r')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open(sys.argv[1]+'.result','w')
process_map(go, lines, max_workers=12, chunksize=1000)

print('All OK\a')
