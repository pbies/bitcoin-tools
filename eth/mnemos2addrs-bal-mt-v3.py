#!/usr/bin/env python3

import mnemonic
import binascii
from web3.auto import w3
from web3 import Web3
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

i = open('input.txt','r')
f = i.readlines()
f = [line.strip() for line in f]
cnt=len(f)

o = open('output.txt','a')

w3.eth.account.enable_unaudited_hdwallet_features()
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

def go(i):
	#seed = mnemonic.Mnemonic.to_seed(i)
	#private_key = mnemonic.Mnemonic.to_hd_master_key(seed)
	try:
		acc = w3.eth.account.from_mnemonic(i)
	except:
		return
	address = w3.to_checksum_address(acc.address)
	bal=w3.eth.get_balance(address,"latest")
	if bal>=1000000000000000:
		#acc = w3.eth.account.from_mnemonic(i)
		h=acc._private_key.hex()
		b='{0:.18f}'.format(bal/1e18)
		o.write(address+" = "+str(b)+" ETH = "+i+" = "+h+"\n")
		o.flush()
		print("\r"+address+" = "+str(b)+" ETH = "+i+" = "+h, flush=True)

process_map(go, f, max_workers=8, chunksize=1000)
