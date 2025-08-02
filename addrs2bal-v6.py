#!/usr/bin/env python3

from tqdm import tqdm
from urllib.request import urlopen
import json
import requests
import time

def check_tx(address):
	txid = []
	cdx = []
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	except:
		try:
			htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
		except:
			return None
	res = json.loads(htmlfile.read())
	funded=res['chain_stats']['funded_txo_sum']
	spent=res['chain_stats']['spent_txo_sum']
	bal=funded-spent
	#print(address+' '+str(bal))
	return bal

def check_bal(address):
	try:
		time.sleep(2)
		r=check_tx(address)
		if not r:
			with open('errors.txt','a') as t:
				t.write(f'{address}\n')
			return None
		i=int(r)/1e8
		return '{0:.8f}'.format(i)+' BTC'
	except:
		return None

def go(k):
	b=str(check_bal(k))
	if b:
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
