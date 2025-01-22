#!/usr/bin/env python3

from tqdm import tqdm
import base64, sys

print('Reading...', flush=True)
i = open("input.txt","r").read().splitlines()

print('Writing...', flush=True)
o = open("output.txt","wb")

for line in tqdm(i):
	w=''
	try:
		w=base64.b64decode(line)
	except:
		pass
	if w!='':
		o.write(w+b'\n')
		o.flush()

print('\a', end='', file=sys.stderr)
