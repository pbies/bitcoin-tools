#!/usr/bin/env python3

# reorder output!

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import binascii
import mnemonic
import os, sys
from multiprocessing import Pool

i = open('input.txt','r').read().splitlines()
o = open('output.txt','w')

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(i):
	address = w3.to_checksum_address(i[0:42])
	try:
		bal=w3.eth.get_balance(address,'latest')
	except:
		try:
			bal=w3.eth.get_balance(address,'latest')
		except:
			return
	b='{0:.18f}'.format(bal/1e18)
	o.write(address+' '+str(b)+' ETH\n')
	o.flush()
	if bal>=1000000000000000:
		print('\n\a'+address+' = '+str(b)+' ETH = '+i, flush=True)

if __name__=='__main__':
	os.system('cls||clear')
	c=0
	cnt=10
	th=4
	max_=len(i)
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, i, chunksize=10):
			if c%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			c=c+1

	print('\a', end='', file=sys.stderr)
