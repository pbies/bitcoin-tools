#!/usr/bin/env python3

from web3 import Web3
from tqdm import tqdm

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/-ixFHz8NzHoGk2OOYc3EPLH9BxZpHfQ_"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# print(w3.is_connected())

outfile = open("output.txt","a")

cnt=sum(1 for line in open("input.txt", 'r'))

def worker(key):
	bal=w3.eth.get_balance(key,"latest")
	b='{0:.18f}'.format(bal/1e18)
	if bal>0:
		outfile.write(key+" = "+str(b)+" ETH\n")
		outfile.flush()

f=open("input.txt","r")
lines=f.readlines()
lines = [x.strip() for x in lines]
lines = [w3.to_checksum_address(x) for x in lines]

for i in tqdm(lines,total=len(lines)):
	worker(i)
