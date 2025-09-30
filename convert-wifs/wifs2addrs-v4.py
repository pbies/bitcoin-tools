#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import base58
import sys

hdwallet = HDWallet(symbol=BTC)

def wif_to_pvk(s): #in: '5HpH... [~51] out: 8000... [66]
	return base58.b58decode_check(s).hex()[2:]

def go(k):
	try:
		hdwallet.from_private_key(private_key=wif_to_pvk(k))
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
lines = infile.readlines()
lines = [x.strip() for x in lines]

print('Writing...', flush=True)
outfile = open(sys.argv[1]+'.result','w')
process_map(go, lines, max_workers=10, chunksize=10000)

print('All OK')
print('\a',end='',file=sys.stderr)
