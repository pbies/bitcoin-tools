#!/usr/bin/env python3

from web3 import Web3
from tqdm.contrib.concurrent import process_map

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# print(w3.is_connected())

outfile = open("output2.txt","a")

cnt=sum(1 for line in open("output.txt", 'r'))

def worker(key):
	bal=w3.eth.get_balance(key,"latest")
	b='{0:.18f}'.format(bal/1e18)
	if bal>0:
		outfile.write(key+" = "+str(b)+" ETH\n")
		outfile.flush()

f=open("output.txt","r")
lines=f.readlines()
lines = [x.strip() for x in lines]
lines = [w3.to_checksum_address(x) for x in lines]

process_map(worker, lines, max_workers=4, chunksize=1000)
