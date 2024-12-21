#!/usr/bin/env python3

from pprint import pprint
import base58
import json
import requests
import time

address_list = open('addrs.txt','r').read().splitlines()
out = open('addrs-bals.txt','w')

for addr in address_list:
	try:
		base58.b58decode_check(addr)
	except:
		continue
	time.sleep(1)
	r=requests.get(f"https://blockstream.info/api/address/{addr}").text
	j=json.loads(r)
	out.write(j)
	out.flush()
