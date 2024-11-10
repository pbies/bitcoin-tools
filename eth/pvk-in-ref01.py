#!/usr/bin/env python3

# final

from mnemonic import Mnemonic
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import base58
import binascii

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

w3 = Web3(Web3.HTTPProvider(alchemy_url))

i=open('ref.txt','r')
o=open('output.txt','a')

lines=i.readlines()
ref = [x.strip() for x in lines]
ref = [w3.to_checksum_address(x) for x in ref]

#print(ref)

def go(i):
	pvk=hex(i)[2:]
	pvk='0'*(64-len(pvk))+pvk

	address = w3.eth.account.from_key(pvk).address
	#address = w3.to_checksum_address(address)
	#print(address,flush=True)

	if address in ref:
		print(f'\n\afound: 0x{pvk}',flush=True)
		o.write(f"Private key: 0x{pvk}\n")
		o.write(f"Address: {address}\n\n")
		o.flush()
	else:
		#print('.',end='',flush=True)
		pass

process_map(go, range(1,1000000), max_workers=8, chunksize=1000)
o.flush()
o.close()
