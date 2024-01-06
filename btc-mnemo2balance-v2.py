#!/usr/bin/env python3

import mnemonic
import binascii
import bip32utils
import time
from tqdm import tqdm
from urllib.request import urlopen
import json

i = open('input.txt','r')
f = i.readlines()
f = [line.strip() for line in f]
cnt=len(f)

def check_tx(address):
	txid = []
	cdx = []
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	except:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	res = json.loads(htmlfile.read())
	funded=res['chain_stats']['funded_txo_sum']
	spent=res['chain_stats']['spent_txo_sum']
	bal=funded-spent
	return bal

for i in tqdm(f,total=cnt):
	seed = mnemonic.Mnemonic.to_seed(i)
	xprv = mnemonic.Mnemonic.to_hd_master_key(seed)
	root_key = bip32utils.BIP32Key.fromExtendedKey(xprv)
	child_key = root_key.ChildKey(0).ChildKey(0)
	address = child_key.Address()
	time.sleep(1)
	bal=check_tx(address)
	if bal>0:
		print(f'\amnemo: {i}\nbalance: {bal}\n',flush=True)
