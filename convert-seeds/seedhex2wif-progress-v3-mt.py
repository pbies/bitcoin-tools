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
from tqdm.contrib.concurrent import process_map

def bip39(seed):
	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(bytes.fromhex(seed))
	bip32_child_key_obj = bip32_root_key_obj.ChildKey(
		84 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(0).ChildKey(0)

	return bip32_child_key_obj.WalletImportFormat()

with open("input.txt","r") as f:
	lines = f.read().splitlines()

o=open("output.txt","w")

def go(line):
	try:
		t=bip39(line)
	except:
		return
	o.write(t+' 0\n')
	o.flush()

process_map(go, lines, max_workers=12, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
