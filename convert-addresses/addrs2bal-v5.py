#!/usr/bin/env python3

from tqdm import tqdm
from urllib.request import urlopen
import json
import requests
import time

def check_bal(address):
	try:
		time.sleep(2)
		r=requests.get('https://blockchain.info/q/addressbalance/'+address)
		if not r.status_code==200:
			with open('errors.txt','a') as t:
				t.write(f'{address}\n')
			return
		i=int(r.text)/1e8
		return '{0:.8f}'.format(i)+' BTC'
	except:
		return None

def go(k):
	b=str(check_bal(k))
	if b:
		outfile.write(k+':'+b+'\n')
		outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

for line in tqdm(lines,total=len(lines)):
	go(line)

import sys
print('\a',end='',file=sys.stderr)
