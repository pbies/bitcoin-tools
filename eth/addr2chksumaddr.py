#!/usr/bin/env python3

from web3 import Web3
from web3.auto import w3
from tqdm import tqdm

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

infile = open('input.txt','r')
f=infile.readlines()
cnt=len(f)
infile.seek(0,0)
outfile = open('output.txt','w')

for i in tqdm(infile,total=cnt):
	a1, a2, a3 = i.strip().split(' ')
	chksum_addr = w3.to_checksum_address(a3[2:])
	outfile.write(a1+' '+a2+' '+chksum_addr+'\n')
	outfile.flush()

infile.close()
outfile.close()

import sys
print('\a',end='',file=sys.stderr)
