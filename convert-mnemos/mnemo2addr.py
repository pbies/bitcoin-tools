#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm

i=open('input.txt','r')

cnt=sum(1 for line in i)

i.seek(0,0)

o=open('output.txt','w')

for j in tqdm(i,total=cnt):
	j=j.strip()
	hdwallet = HDWallet(symbol=BTC)
	try:
		hdwallet.from_mnemonic(j)
	except:
		continue
	o.write(hdwallet.p2pkh_address()+'\n')
	o.flush()
