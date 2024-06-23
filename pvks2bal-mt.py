#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from urllib.request import urlopen
import json
import sys
import time

hdwallet = HDWallet(symbol=BTC)

def check_bal(address):
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	except:
		return None
	else: 
		res = json.loads(htmlfile.read())
		funded=res['chain_stats']['funded_txo_sum']
		spent=res['chain_stats']['spent_txo_sum']
		bal=funded-spent
		return bal

def go(k):
	try:
		hdwallet.from_private_key(private_key=k)
	except:
		return
	outfile.write(hdwallet.wif()+'\n')
	b1=str(check_bal(hdwallet.p2pkh_address()))
	outfile.write(hdwallet.p2pkh_address()+' : '+b1+'\n')
	b2=str(check_bal(hdwallet.p2sh_address()))
	outfile.write(hdwallet.p2sh_address()+' : '+b2+'\n')
	b3=str(check_bal(hdwallet.p2wpkh_address()))
	outfile.write(hdwallet.p2wpkh_address()+' : '+b3+'\n')
	b4=str(check_bal(hdwallet.p2wpkh_in_p2sh_address()))
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+' : '+b4+'\n')
	b5=str(check_bal(hdwallet.p2wsh_address()))
	outfile.write(hdwallet.p2wsh_address()+' : '+b5+'\n')
	b6=str(check_bal(hdwallet.p2wsh_in_p2sh_address()))
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+' : '+b6+'\n\n')
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=10, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
