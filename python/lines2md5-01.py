#!/usr/bin/env python3

from tqdm import tqdm
import hashlib
import sys

o=open('output.txt','w')

for i in tqdm(open('input.txt','rb').read().splitlines()):
	o.write(f'{hashlib.md5(i).hexdigest()}\n')

print('\a', end='', file=sys.stderr)
