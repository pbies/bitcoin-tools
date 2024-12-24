#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from tqdm.contrib.concurrent import process_map
import base58
import os

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

a=open('wifs-addrs.txt','w')
b=open('addrs.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(x):
	c=os.urandom(32)
	d=c.hex()
	e='0'*(64-len(d))+d
	hdwallet.from_private_key(private_key=e)
	wif=pvk_to_wif2(e)
	f=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	a.write(f)
	a.flush()
	g=hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	b.write(g)
	b.flush()

r=range(1,int(1e7)+1)
process_map(go, r, max_workers=16, chunksize=1000)

import sys
print('\a', end='', file=sys.stderr)
