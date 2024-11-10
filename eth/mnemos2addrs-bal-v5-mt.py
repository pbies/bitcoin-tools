#!/usr/bin/env python3

import mnemonic
import binascii
from web3.auto import w3
from web3 import Web3
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

i = open('input.txt','r')
f = i.readlines()
i.seek(0,0)
m=[]
for j in range(len(f)):
	f[j]=f[j].strip()
	m.append(f[j])
cnt=len(f)

o = open('output.txt','a')

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(i):
	try:
		acc = w3.eth.account.from_mnemonic(i)
	except:
		return
	address = w3.to_checksum_address(acc.address)
	bal=w3.eth.get_balance(address,'latest')
	h=acc._private_key.hex()
	b='{0:.18f}'.format(bal/1e18)
	o.write(address+' = '+str(b)+' ETH = '+i+' = '+h+'\n')
	o.flush()
	if bal>=1000000000000000:
		print('\n\a'+address+' = '+str(b)+' ETH = '+i+' = '+h, flush=True)

process_map(go, m, max_workers=10, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
