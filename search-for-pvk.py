#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import numpy as np
import pandas as pd

hdwallet = HDWallet(symbol=BTC)

pvk1 = 0x414ebfe886361d9e9cb2f5d46bfe1c3f1523fe80830600000000000000000000
pvk2 = 0x414ebfe886361d9e9cb2f5d46bfe1c3f1523fe808306ffffffffffffffffffff
comp = hex(0x03f31ec8aae7bda56cd61a5e464a0ed84d8813db3cfa3dc91261d6701893ba70ae)[2:]
uncomp = hex(0x04f31ec8aae7bda56cd61a5e464a0ed84d8813db3cfa3dc91261d6701893ba70ae94ee1d6b4267a2a66512ac81302bacec84e0e7f330858fa5ca43e5e6f743ff17)[2:]

def range(start, stop):
	i = start
	while i < stop:
		yield i
		i += 1

def go(i):
	if i%65536==0:
		print(hex(i),end='\r')
	j=hex(i)[2:]
	k='0'*(64-len(j))+j
	pvk=hdwallet.from_private_key(private_key=k)
	pubkey=hdwallet.compressed()
	if pubkey==comp:
		print(f'\npvk: {i}\n')
		o=open('FOUND.txt','a')
		o.write(f'pvk: {i}\n')
		o.flush()
		o.close()

print('starting...')
process_map(go, range(pvk1,pvk2), max_workers=8, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
