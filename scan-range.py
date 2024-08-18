#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import sys

hdwallet = HDWallet(symbol=BTC)

def growing_range(mid,x):
	start=mid-x
	end=mid+x
	rng = [0] * (x*2-1)
	rng[::2], rng[1::2] = range(mid, end), range(mid-1, start, -1)
	return rng

def int2pvkhex(a):
	b=hex(a)[2:]
	return '0'*(64-len(b))+b

def go(i):
	hdwallet.from_private_key(private_key=int2pvkhex(i))
	if hdwallet.p2pkh_address()=='1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps':
		print()
		print(f'pvk int: {i}')
		print(f'pvk hex: {hex(i)}')
		print(f'WIF: {hdwallet.wif()}')
		print('\a')
		o=open('KEYFOUNDKEYFOUND.txt','a')
		o.write('\n')
		o.write('pvk int: '+str(i)+'\n')
		o.write('pvk hex: '+hex(i)+'\n')
		o.write('WIF: '+hdwallet.wif()+'\n')
		o.write('\n')
		o.flush()
		o.close()
		sys.exit(0)

r=growing_range(0x3d940000,int(1e8))
process_map(go, r, max_workers=8, chunksize=1000)

print('Done!\a')
