#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from pprint import pprint
from tqdm import tqdm

mnemos=open('input.txt','r')

cnt=sum(1 for line in open("input.txt", 'r'))

o=open('output.txt','w')

for m in tqdm(mnemos,total=cnt):
	m=m.rstrip('\n')
	hdwallet = HDWallet(symbol=BTC)
	try:
		hdwallet.from_mnemonic(mnemonic=m)
	except:
		continue
	hdwallet.from_path(path="m/84'/0'/0'/0/0")
	o.write(hdwallet.p2sh_address())
	o.write('\n')
	o.write(hdwallet.p2wpkh_address())
	o.write('\n')
	o.write(hdwallet.p2wsh_address())
	o.write('\n')
	o.write(hdwallet.p2pkh_address())
	o.write('\n')
	o.flush()
