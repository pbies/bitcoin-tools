#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import pprint
import random

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

hdwallet = HDWallet(symbol=BTC)

def go(k):
	try:
		hdwallet.from_mnemonic(k)
	except:
		return
	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk)
	w=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n'+hdwallet.p2sh_address()+'\n'+hdwallet.p2wpkh_address()+'\n'+hdwallet.p2wpkh_in_p2sh_address()+'\n'+hdwallet.p2wsh_address()+'\n'+hdwallet.p2wsh_in_p2sh_address()+'\n\n'
	outfile.write(w)
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

print('Reading...', flush=True)
lines = infile.read().splitlines()

print('Writing...', flush=True)
process_map(go, lines, max_workers=12, chunksize=1000)

import sys
print('\a', end='', file=sys.stderr)
