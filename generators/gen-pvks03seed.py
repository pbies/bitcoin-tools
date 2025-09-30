#!/usr/bin/env python3

import os, sys, random
from tqdm import tqdm

o=open('output.txt','w')

count=1000000

def go():
	o.write(f'{hex(random.randint(1, 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140))[2:].zfill(64)}\n')
	o.flush

for j in range(0, 100):
	random.seed(j)
	for i in tqdm(range(0, count)):
		go()

print('\a', end='', file=sys.stderr)
