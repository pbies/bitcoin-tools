#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import base58
import binascii
import hashlib
import mnemonic
import os
import sys

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(m):
	n=m.decode()
	try:
		acc = w3.eth.account.from_mnemonic(n)
	except:
		return
	a = w3.to_checksum_address(acc.address)
	p = acc._private_key.hex()
	with open('output.txt','a') as o:
		o.write(f'{a} {p} {n}\n')

th=28

def main():
	print('Reading...', flush=True)
	infile = open('input.txt','rb').read().splitlines()
	i=len(infile)
	tmp = 0
	cnt = 1000
	th=28
	print('Writing...', flush=True)
	o = open('output.txt','w')
	with Pool(processes=th) as p, tqdm(total=i) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			if tmp%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			tmp=tmp+1

	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
