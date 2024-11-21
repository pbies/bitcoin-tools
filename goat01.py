#!/usr/bin/env python3

import hashlib
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import sys

hdwallet = HDWallet(symbol=BTC)

def sha(k):
	sha = hashlib.sha256()
	sha.update(k)
	return sha.hexdigest()

outfile = open('output.txt','w')

def go(i):
	#if i%100000==0:
	#	print(i,end='\r')
	a=hex(i)[2:]
	b=sha(a.encode())
	c=b[0:32]
	d=hdwallet.from_entropy(c)

	r=hdwallet.wif()+'\n'
	r+=hdwallet.p2pkh_address()+'\n'
	r+=hdwallet.p2sh_address()+'\n'
	r+=hdwallet.p2wpkh_address()+'\n'
	r+=hdwallet.p2wpkh_in_p2sh_address()+'\n'
	r+=hdwallet.p2wsh_address()+'\n'
	r+=hdwallet.p2wsh_in_p2sh_address()+'\n\n'

	outfile.write(r)
	outfile.flush()

process_map(go, range(0,2**28+1), max_workers=24, chunksize=10000)

print()
print('\a', end='', file=sys.stderr)

"""
1. generate 0 - 2^32 numbers in hex
2. hash them with sha256
3. delete last 32 characters from that hash and use the rest as bip 39 mnemonic entropy
4. generate wallets 
5. check them for balance

m/49'/0'/0'/0
! m/84'/0'/0'/0
m/44'/60'/0'/0 this one is ETH
"""
