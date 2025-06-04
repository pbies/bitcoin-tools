#!/usr/bin/env python3

from tqdm import tqdm
from web3 import Web3
from web3.auto import w3
import sys

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/-ixFHz8NzHoGk2OOYc3EPLH9BxZpHfQ_"
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

print('Reading...', flush=True)
infile = open('eth250311sorted-addrs-only.txt','r').read().splitlines()
cnt=len(infile)
outfile = open('chksum-addrs.txt','w')

print('Writing...', flush=True)
for i in tqdm(infile, total=cnt):
	chksum_addr = w3.to_checksum_address(i)
	outfile.write(f'{chksum_addr}\n')
	outfile.flush()

infile.close()
outfile.close()

print('\a', end='', file=sys.stderr)
