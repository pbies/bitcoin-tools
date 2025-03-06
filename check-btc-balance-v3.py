#!/usr/bin/env python3

from pprint import pprint
import base58
import json
import requests
import time

address_list = open('addrs.txt','r').read().splitlines()
out = open('addrs-bals.txt','w')

for addr in address_list:
	time.sleep(1)
	r=requests.get(f"https://blockstream.info/api/address/{addr}").text
	j=json.loads(r)
	funded=j['chain_stats']['funded_txo_sum']
	spent=j['chain_stats']['spent_txo_sum']
	bal=funded-spent
	tmp=addr+'\t'+'{0:.8f}'.format(bal/100000000)+' BTC\n'
	print(tmp, end='')
	out.write(tmp)
	out.flush()
