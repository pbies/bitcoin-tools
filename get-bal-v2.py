#!/usr/bin/env python3

import json
from urllib.request import urlopen

def check_tx(address):
	txid = []
	cdx = []
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	except:
		print('Unable to connect internet to fetch RawTx. Exiting..')
		sys.exit(1)
	else: 
		res = json.loads(htmlfile.read())
		funded=res['chain_stats']['funded_txo_sum']
		spent=res['chain_stats']['spent_txo_sum']
		bal=funded-spent
		return bal

for a in open('04addrs.txt','r'):
	a=a.strip()
	b=check_tx(a)
	print(a+'\t'+'{0:.8f}'.format(b/100000000)+' BTC',flush=True)
