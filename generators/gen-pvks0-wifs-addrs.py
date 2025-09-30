#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
from hdwallet import HDWallet
from hdwallet.symbols import BTC

hdwallet = HDWallet(symbol=BTC)

a=open('wifs-addrs.txt','w')
b=open('addrs.txt','w')

def go(x):
	y=hex(x)[2:]
	z='0'*(64-len(y))+y
	hdwallet.from_private_key(private_key=z)
	a.write(hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n')
	a.write(hdwallet.p2sh_address()+'\n')
	a.write(hdwallet.p2wpkh_address()+'\n')
	a.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	a.write(hdwallet.p2wsh_address()+'\n')
	a.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	a.flush()
	b.write(hdwallet.p2pkh_address()+'\n')
	b.write(hdwallet.p2sh_address()+'\n')
	b.write(hdwallet.p2wpkh_address()+'\n')
	b.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	b.write(hdwallet.p2wsh_address()+'\n')
	b.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	b.flush()

r=range(1,int(1e7)+1)
process_map(go, r, max_workers=8, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
