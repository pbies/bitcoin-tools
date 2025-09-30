#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
from hdwallet import HDWallet
from hdwallet.symbols import BTC
import base58

hdwallet = HDWallet(symbol=BTC)

o=open('output.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def go(x):
	y=hex(x)[2:]
	z='0'*(64-len(y))+y
	o.write(pvk_to_wif2(z).decode()+' 0 # '+z+'\n')
	o.flush()

r=range(1,int(1e7)+1)
process_map(go, r, max_workers=8, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
