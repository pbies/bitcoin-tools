#!/usr/bin/env python3

import base58
import hashlib
import sys
import bip32utils
from tqdm import tqdm

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

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

i = open("input.txt","r")
o = open("output.txt","w")

cnt=sum(1 for line in i)

i.seek(0,0)

for j in tqdm(i,total=cnt):
	j=j.strip()
	if len(j)==64:
		o.write(pvk_to_wif2(j).decode('ascii')+"\n")
		o.flush()
	if len(j)==128:
		o.write(bip39(j)+"\n")
		o.flush()
