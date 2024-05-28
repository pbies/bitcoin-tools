#!/usr/bin/env python3

from urllib.request import urlopen
import json
import sys
import time

def check_tx(address):
	txid = []
	cdx = []
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

o=open('output.txt','a')

for a in open('input.txt','r'):
	a=a.strip()
	time.sleep(1)
	b=check_tx(a)
	if b!=None:
		tmp=a+'\t'+'{0:.8f}'.format(b/100000000)+' BTC'
		print(tmp,flush=True)
		o.write(tmp+'\n')
		o.flush()
