#!/usr/bin/env python3

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

import pprint
import binascii
import mnemonic
import bip32utils
from tqdm import tqdm
from hdwallet import HDWallet
from hdwallet.symbols import BTC

with open("input.txt","r") as f:
	lines = f.readlines()

lines = [x.strip() for x in lines]
cnt=len(lines)

with open("output.txt","w") as o:
	for line in tqdm(lines,total=cnt):
		hdwallet = HDWallet(symbol=BTC)
		hdwallet.from_seed(seed=line)
		o.write(hdwallet.wif()+'\n')
		o.write(hdwallet.p2pkh_address()+'\n')
		o.write(hdwallet.p2sh_address()+'\n')
		o.write(hdwallet.p2wpkh_address()+'\n')
		o.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
		o.write(hdwallet.p2wsh_address()+'\n')
		o.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')

import sys
print('\a',end='',file=sys.stderr)
