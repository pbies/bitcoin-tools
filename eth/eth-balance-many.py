#!/usr/bin/env python3

from tqdm import tqdm
from web3 import Web3

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

i=open('input.txt')
o=open('output.txt','w')

cnt=sum(1 for line in open("input.txt", 'r'))

for addr in tqdm(i, total=cnt):
	addr=addr.strip()
	cksum=Web3.to_checksum_address(addr)
	bal=w3.eth.get_balance(cksum)
	o.write('addr: '+addr+' balance: '+str(bal)+'\n')
	o.flush()
