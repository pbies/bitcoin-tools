#!/usr/bin/env python3

import os, sys
from tqdm import tqdm

o=open('output.txt','w')

count=1000000

def go():
	o.write(f'{os.urandom(32).hex()}\n')
	o.flush

for i in tqdm(range(0,count)):
	go()

print('\a', end='', file=sys.stderr)
