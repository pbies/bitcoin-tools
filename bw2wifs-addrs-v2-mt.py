#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import hashlib, base58
import sys

hdwallet = HDWallet(symbol=BTC)

infile = open('input.txt','rb').read().splitlines()
outfile = open('output.txt','w')

def go(k):
	sha=hashlib.sha256(k).hexdigest()
	hdwallet.from_private_key(sha)
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

process_map(go, infile, max_workers=20, chunksize=10000)

print('\a', end='', file=sys.stderr)
