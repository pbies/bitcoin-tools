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

outfile=open('result.txt','w')

for addr in addrs:
	print('Testing '+addr+'...',end='')
	result=limited('https://blockchain.info/q/addressbalance/'+addr)
	if result.status_code == 429:
		print('error 429 - too many requests!\a')
		input('Press Enter to quit...\n')
		exit()
	print('result='+result.text)
	i=int(result.text)
	if i > 0:
		outfile.write(addr+':'+result.text+'\n')
		outfile.flush()

print('=== Script finished ===\a')
input('Press Enter to quit...\n')
