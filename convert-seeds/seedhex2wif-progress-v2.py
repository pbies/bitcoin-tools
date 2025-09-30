#!/usr/bin/env python3

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

# not error secure, don't use this script!

import pprint
import binascii
import mnemonic
import bip32utils
from tqdm import tqdm

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

with open("output.txt","w") as o:
	for line in tqdm(lines):
		try:
			t=bip39(line)
		except:
			continue
		o.write(t+' 0\n')
		o.flush()

import sys
print('\a',end='',file=sys.stderr)
