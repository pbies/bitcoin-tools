#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import binascii
import mnemonic
import os, sys
from multiprocessing import Pool

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(i):
	i=i.decode()[:-1]
	address = w3.to_checksum_address(i[0:42])
	#pvk=i[43:]
	try:
		bal=w3.eth.get_balance(address,'latest')
	except:
		try:
			bal=w3.eth.get_balance(address,'latest')
		except:
			t=open('errors.txt','a')
			t.write(f'{i}\n')
			t.flush()
			t.close()
			return
	b='{0:.18f}'.format(bal/1e18)
	o = open('output.txt','a')
	o.write(f'{str(b)} ETH {i}\n')
	o.flush()
	if bal>=int(1e15):
		print(f'\n\a{i} {str(b)} ETH', flush=True)

if __name__=='__main__':
	os.system('cls||clear')
	size = os.path.getsize('input.txt')
	i = open('input.txt','rb')
	if os.path.exists("output.txt"):
		os.remove("output.txt")
	t=i.tell()
	tmp = 0
	c=0
	cnt=1000
	th=4
	with Pool(processes=th) as p, tqdm(total=size) as pbar:
		for result in p.imap_unordered(go, i, chunksize=10):
			t=i.tell()
			r=t-tmp
			if r>cnt:
				tmp=t
				pbar.update(r)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)
