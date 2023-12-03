#!/usr/bin/env python3

import requests
import time

i=open('input.txt')

for addr in i:
	addr=addr.strip()
	time.sleep(3)
	r=requests.get('https://blockchain.info/q/addressbalance/'+addr)

	if not r.status_code==200:
		print('Error',r.status_code)
		exit(1)

	b=int(r.text)

	print(addr,'\t',r.text,'sat\t',b/100000,'mBTC\t',b/100000000,'BTC', flush=True)
