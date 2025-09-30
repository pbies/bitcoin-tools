#!/usr/bin/env python3

from bitcoin import *
from tqdm.contrib.concurrent import process_map
import base58
from hdwallet import HDWallet
from hdwallet.symbols import BTC

outfile = open("wif-output.txt","w")

hdwallet = HDWallet(symbol=BTC)

def worker(key):
	try:
		hdwallet.from_wif(key)
	except:
		return
	outfile.write(key+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n')
	outfile.flush()

with open("wif.txt","r") as f:
	process_map(worker, f.readlines(), max_workers=4, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
