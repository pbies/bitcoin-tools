#!/usr/bin/env python3

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
e = open('errors.txt','w')

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(i):
	tmp=i.split(' ')
	address = w3.to_checksum_address(tmp[1])
	pvk = tmp[0]
	try:
		bal=w3.eth.get_balance(address,'latest')
	except:
		try:
			bal=w3.eth.get_balance(address,'latest')
		except:
			e.write(f'{address} {pvk}\n')
			e.flush()
			return
	b='{0:.18f}'.format(bal/1e18)
	o.write(str(b)+' '+address+' '+pvk+'\n')
	o.flush()
	if bal>=1000000000000000:
		print(f'\n\a{pvk} {address} {str(b)} ETH', flush=True)

if __name__=='__main__':
	os.system('cls||clear')
	c=0
	cnt=10
	th=2
	max_=len(i)
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, i, chunksize=10):
			if c%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			c=c+1

	print('\a', end='', file=sys.stderr)
