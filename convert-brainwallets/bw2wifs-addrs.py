#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import hashlib, base58
from cryptotools import PrivateKey
import sys

hdwallet = HDWallet(symbol=BTC)

def go(k):
	pwd=k.rstrip(b'\n')
	sha=hashlib.sha256(pwd).digest()
	tmp=b'\x80'+sha
	wif=base58.b58encode_check(tmp)
	wif2=wif.decode('ascii')
	prv = PrivateKey.from_wif(wif2).hex()
	try:
		hdwallet.from_private_key(prv)
	except:
		return
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

infile = open('input.txt','rb')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=4, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
