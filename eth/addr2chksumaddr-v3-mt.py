#!/usr/bin/env python3

from tqdm import tqdm
from web3 import Web3
from web3.auto import w3
import sys, os
from multiprocessing import Pool

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/-ixFHz8NzHoGk2OOYc3EPLH9BxZpHfQ_"
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

print('Reading...', flush=True)
infile = open('eth250311sorted-addrs-only.txt','rb')
size = os.path.getsize('eth250311sorted-addrs-only.txt')
outfile = open('chksum-addrs.txt','w')
th=16

print('Writing...', flush=True)

def go(i):
	i=i.rstrip(b'\n').decode()
	chksum_addr = w3.to_checksum_address(i)
	outfile.write(f'{chksum_addr}\n')
	outfile.flush()

i=infile.tell()
tmp = 0
cnt = 1000

if __name__=='__main__':
	pbar=tqdm(total=size)
	with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			i=infile.tell()
			r=i-tmp
			if r>cnt:
				tmp=i
				pbar.update(r)
				pbar.refresh()

	infile.close()
	outfile.close()

	print('\a', end='', file=sys.stderr)
