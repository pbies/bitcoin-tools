#!/usr/bin/env python3

import requests
from ratelimiter import RateLimiter

print('=== Starting script ===')

@RateLimiter(max_calls=1, period=10)
def limited(req):
	return requests.get(req)

with open('addrs.txt','r') as f:
	addrs = f.readlines()
	addrs = [x.rstrip('\n') for x in addrs]

for addr in addrs:
	print('Testing '+addr+'...',end='')
	result=limited('https://blockchain.info/q/addressbalance/'+addr)
	if result.status_code == 429:
		print('error 429 - too many requests!')
		input('Press Enter to quit...')
		exit()
	print('result=\n'+result.text)

print('=== Script finished ===')
input('Press Enter to quit...')
