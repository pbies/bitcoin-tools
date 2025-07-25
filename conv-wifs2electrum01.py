#!/usr/bin/env python3

import sys, os, datetime
from tqdm import tqdm

os.system('cls' if os.name == 'nt' else 'clear')
print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

i=open('input.txt','r').read().splitlines()
o=open('output.txt','w')

for x in tqdm(i):
	a=''
	if x:
		a=x[0]
	if a=='5' or a=='K' or a=='L':
		o.write(f'p2pkh:{x}\np2wpkh:{x}\np2wpkh-p2sh:{x}\n')

print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('\a', end='', file=sys.stderr)
