#!/usr/bin/env python3

from mnemonic import Mnemonic
from tqdm import tqdm
import binascii
import bip32utils
import mnemonic
import pprint

mnemo = Mnemonic("english")

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
	lines = f.readlines()

lines = [x.strip() for x in lines]
cnt=len(lines)

o=open("output.txt","w")

for line in tqdm(lines,total=cnt):
	try:
		seed=mnemo.to_seed(line).hex()
		wif=bip39(seed)
		# print(pvk)
		o.write(wif+' 0\n')
		o.flush()
	except:
		continue
