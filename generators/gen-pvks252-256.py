#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
from hdwallet import HDWallet
from hdwallet.symbols import BTC

hdwallet = HDWallet(symbol=BTC)

o=open('output.txt','w')

def go(x):
	y=hex(x)[2:]
	z='0'*(64-len(y))+y
	hdwallet.from_private_key(private_key=z)
	o.write(hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n')
	o.write(hdwallet.p2sh_address()+'\n')
	o.write(hdwallet.p2wpkh_address()+'\n')
	o.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	o.write(hdwallet.p2wsh_address()+'\n')
	o.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	o.flush()

r=range(2**252,2**252+1000000)
process_map(go, r, max_workers=8, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
