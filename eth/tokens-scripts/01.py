#!/usr/bin/env python3

from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import json
import pprint
import requests
import sys
import time

url='https://eth-mainnet.g.alchemy.com/v2/'

i=open('input.txt','r').read().splitlines()
o=open('output.txt','w')

cnt = len(i)

r=[]

def go(addr):
	addr2=addr.strip().split(',')[0]
	payload = {
		"id": 1,
		"jsonrpc": "2.0",
		"method": "alchemy_getTokenBalances",
		"params": [addr2]
	}
	headers = {
		"accept": "application/json",
		"content-type": "application/json"
	}

	resp = requests.post(url, json=payload, headers=headers)
	a=resp.json()
	with open('output.txt','a') as o:
		try:
			c=a['result']['tokenBalances']
		except:
			o.write('error here\n')
			return
		for d in c:
			if int(d['tokenBalance'],16)>0:
				o.write(addr)
				o.write(',')
				o.write(d['contractAddress'])
				o.write(',')
				e=str(int(d['tokenBalance'],16))
				o.write(e)
				o.write('\n')

process_map(go, i, max_workers=4, chunksize=10)

print('\a',end='',file=sys.stderr)
