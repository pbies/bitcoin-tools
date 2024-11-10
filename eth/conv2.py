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

for a in tqdm(i,total=cnt):
	if a[:-1]=='error here':
		continue
	elif a[-2]==':':
		global mainaddr
		mainaddr=a[:-2]
		#print(mainaddr)
		continue
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

i.close()
o.close()

import sys
print('\a',end='',file=sys.stderr)
