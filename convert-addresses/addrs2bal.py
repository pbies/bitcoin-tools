#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

#from hdwallet import HDWallet
#from hdwallet.symbols import BTC
#from tqdm.contrib.concurrent import process_map
from urllib.request import urlopen
from tqdm import tqdm
import json
#import sys
#import time

#hdwallet = HDWallet(symbol=BTC)

def check_bal(address):
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 5)
	except:
		return None
	else: 
		res = json.loads(htmlfile.read())
		funded=res['chain_stats']['funded_txo_sum']
		spent=res['chain_stats']['spent_txo_sum']
		bal=funded-spent
		return bal

def go(k):
	b=str(check_bal(k))
	outfile.write(k+':'+b+'\n')
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

for line in tqdm(lines,total=len(lines)):
	go(line)

import sys
print('\a',end='',file=sys.stderr)
