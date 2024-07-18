#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from urllib.request import urlopen
from tqdm import tqdm
import json
import sys
import time

hdwallet = HDWallet(symbol=BTC)

def check_bal(address):
	time.sleep(1)
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 2)
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
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

infile = open('pvks.txt','r')
outfile = open('pvks-out.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

for line in tqdm(lines,total=len(lines)):
	go(line)

import sys
print('\a',end='',file=sys.stderr)
