#!/usr/bin/env python3

import requests

print('=== Starting script ===')

with open('addrs.txt','r') as f:
	addrs = f.readlines()
	addrs = [x.rstrip('\n') for x in addrs]

for addr in addrs:
	print('Testing '+addr+'...',end='')
	result=requests.get('https://blockchain.info/q/addressbalance/'+addr)
	if result.status_code == 429:
		print('error 429 - too many requests!')
		input('Press Enter to quit...')
		exit()
	print('result='+str(result))

print('=== Script finished ===')
input('Press Enter to quit...')
