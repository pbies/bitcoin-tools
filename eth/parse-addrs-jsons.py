#!/usr/bin/env python3

# https://docs.alchemy.com/reference/alchemy-gettokenbalances

import requests
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from pprint import pprint
import json

url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'

cnt = sum(1 for line in open("input.txt", 'r'))

input_file=open('input.txt','r')
o=open('output.txt','a')

def go(a):
	line=a.strip()

	addr=line[:42]
	j1=line[43:]
	j2=json.loads(j1)['result']
	addr2=j2['address']
	for i in j2['tokenBalances']:
		ca=i['contractAddress']
		tb=str(int(i['tokenBalance'][2:],16))
		if tb!='0':
			o.write('address:'+addr+' contractaddress:'+ca+' balance:'+tb+'\n')

	o.flush()

process_map(go, input_file, max_workers=10, chunksize=10000)

o.close()

import sys
print('\a',end='',file=sys.stderr)
