#!/usr/bin/env python3

from tqdm import tqdm

i=open('input.txt','r') # seeds
o=open('output.txt','w')

lines=i.readlines()
ref = [x.strip() for x in lines]
cnt=len(ref)

for l in tqdm(ref,total=cnt):
	o.write(l[0:64]+'\n')
	o.write(l[64:]+'\n')
	o.flush()

import sys
print('\a',end='',file=sys.stderr)
