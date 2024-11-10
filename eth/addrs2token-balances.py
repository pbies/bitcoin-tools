#!/usr/bin/env python3

from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import json
import pprint
import requests
import time

url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'

i=open('input.txt','r').readlines()
o=open('output.txt','w')

cnt = sum(1 for line in open("input.txt", 'r'))

def go(addr):
	addr=addr.strip()
	payload = {
		"id": 1,
		"jsonrpc": "2.0",
		"method": "alchemy_getTokenBalances",
		"params": [addr]
	}
	headers = {
		"accept": "application/json",
		"content-type": "application/json"
	}

	resp = requests.post(url, json=payload, headers=headers)
	a=resp.json()
	o.write(addr)
	o.write(':\n')
	try:
		c=a['result']['tokenBalances']
	except:
		o.write('error here\n')
		return
	for d in c:
		o.write('\t')
		o.write(d['contractAddress'])
		o.write(':')
		e=str(int(d['tokenBalance'],16))
		o.write(e)
		o.write('\n')
	o.flush()

process_map(go, i, max_workers=6, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
