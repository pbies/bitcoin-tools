#!/usr/bin/env python3

import json
import requests
from pprint import pprint

skip=0
i=open('log.txt','r')
for l in i:
	if 'mempool_stats' in l:
		skip=3
		continue
	if skip>0:
		skip=skip-1
		continue
	if 'address' in l:
		a=l
	if 'funded_txo_sum' in l:
		b1=l
	if 'spent_txo_sum' in l:
		b2=l
	if '}}' in l:
		addr=a[13:-3]
		bal1=b1[b1.find(': ')+2:-2]
		bal2=b2[b2.find(': ')+2:-2]
		if bal1!=bal2:
			print(addr+':'+bal1+':'+bal2)
