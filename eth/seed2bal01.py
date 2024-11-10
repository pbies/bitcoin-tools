#!/usr/bin/env python3

from mnemonic import Mnemonic
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import base58
import binascii
from tqdm import tqdm

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

w3 = Web3(Web3.HTTPProvider(alchemy_url))

i=open('input.txt','r') # seeds
o=open('output.txt','a')

lines=i.readlines()
ref = [x.strip() for x in lines]
#ref = [w3.to_checksum_address(x) for x in ref]
cnt=len(ref)

mnemonic=Mnemonic("english")

def go(i):
	xprv = mnemonic.to_hd_master_key(binascii.unhexlify(i))
	pvk = base58.b58decode_check(xprv)[-32:]

	address = w3.eth.account.from_key(pvk).address
	checksum_address = w3.to_checksum_address(address)

	bal=w3.eth.get_balance(checksum_address,"latest")

	b='{0:.18f}'.format(bal/1e18)
	o.write(f"seed:\n{i}\nchksum address: {checksum_address}\nbalance: {b} ETH\n\n")
	o.flush()
	if bal>0:
		print(f"\n\aseed:\n{i}\nchksum address: {checksum_address}\nbalance: {b} ETH\n")

for i in tqdm(ref,total=cnt):
	go(i)
