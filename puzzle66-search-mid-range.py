#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm

hdwallet = HDWallet(symbol=BTC)

p=0x000000000000000000000000000000000000000000000001a838b13505b26867
middle=p*2
mid=1000000

for i in tqdm([x for i in range(mid) for x in {middle-i:0,middle+i:0}]):
	b=hex(i)
	b='0'*(66-len(b))+b[2:]
	hdwallet.from_private_key(private_key=b)
	a=hdwallet.p2pkh_address()
	if a=='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so':
		print('private key: 0x'+b+'\a')
		exit()

import sys
print('\a',end='',file=sys.stderr)
