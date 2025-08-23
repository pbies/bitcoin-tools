#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import binascii
import mnemonic

i = open('input.txt','r').read().splitlines()
o = open('output.txt','w')

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(i):
	address = i
	try:
		bal=w3.eth.get_balance(address,'latest')
	except:
		return
	b='{0:.18f}'.format(bal/1e18)
	o.write(address+' '+str(b)+' ETH\n')
	o.flush()
	if bal>=1000000000000000:
		print('\n\a'+address+' = '+str(b)+' ETH = '+i, flush=True)

process_map(go, i, max_workers=10, chunksize=1000)

import sys
print('\a', end='', file=sys.stderr)
