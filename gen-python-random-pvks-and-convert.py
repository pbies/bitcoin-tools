#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, base58, random

hdwallet = HDWallet(symbol=BTC)

o=open('output.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

for i in range(0,1000):
	random.seed(i)
	for j in range(0,100000):
		k=hex(random.randint(0,0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140))[2:]
		l='0'*(64-len(k))+k
		try:
			hdwallet.from_private_key(private_key=l)
		except:
			continue
		wif=pvk_to_wif2(l)
		a=f'{wif}\n{hdwallet.wif()}\n{hdwallet.p2pkh_address()}\n{hdwallet.p2sh_address()}\n{hdwallet.p2wpkh_address()}\n{hdwallet.p2wpkh_in_p2sh_address()}\n{hdwallet.p2wsh_address()}\n{hdwallet.p2wsh_in_p2sh_address()}\n\n'
		o.write(a)
		o.flush()

print('\a', end='', file=sys.stderr)
