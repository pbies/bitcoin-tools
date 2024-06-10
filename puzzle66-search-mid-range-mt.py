#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

middle=0x000000000000000000000000000000000000000000000001a838b13505b26867*2
mid=1000000

def go(i):
	b=hex(i)
	b='0'*(66-len(b))+b[2:]
	hdwallet.from_private_key(private_key=b)
	a=hdwallet.p2pkh_address()
	if a=='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so':
		print('private key: 0x'+b+'\a')
		exit()

process_map(go, [x for i in range(mid) for x in {middle-i:0,middle+i:0}], max_workers=10, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
