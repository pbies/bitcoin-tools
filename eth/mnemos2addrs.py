#!/usr/bin/env python3

import mnemonic
import binascii
from web3.auto import w3
from web3 import Web3
from tqdm import tqdm

i = open('input.txt','r')
f = i.readlines()
f = [line.strip() for line in f]
cnt=len(f)

o = open('output.txt','w')

w3.eth.account.enable_unaudited_hdwallet_features()
# alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
# w3 = Web3(Web3.HTTPProvider(alchemy_url))

for i in tqdm(f,total=cnt):
	#seed = mnemonic.Mnemonic.to_seed(i)
	#private_key = mnemonic.Mnemonic.to_hd_master_key(seed)
	try:
		acc = w3.eth.account.from_mnemonic(i)
	except:
		continue
	address = acc.address
	o.write(w3.to_checksum_address(address))
	o.write('\n')
	o.flush()
