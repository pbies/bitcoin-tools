#!/usr/bin/env python3

from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import json
import requests
import time

cnt = sum(1 for line in open("input.txt", 'r'))

i=open('input.txt','r').readlines()
o=open('output.txt','a')

global mainaddr

def go(a):
	if a[:-1]=='error here':
		return
	elif a[-2]==':':
		global mainaddr
		mainaddr=a[:-2]
		#print(mainaddr)
		return
	else:
		b=a[1:43]
		c=int(a[44:-1])
		if c>0:
			try:
				mainaddr
			except:
				continue
			else:
				o.write(mainaddr+' '+b+'\n')
	o.flush()

process_map(go, i, max_workers=4, chunksize=100)

i.close()
o.close()

import sys
print('\a',end='',file=sys.stderr)
