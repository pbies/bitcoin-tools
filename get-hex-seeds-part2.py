#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib
import pprint
import binascii
import mnemonic
import bip32utils

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

outfile = open("output.txt","w")

cnt=sum(1 for line in open("tmp2.txt", 'r'))

with open("tmp2.txt","r") as f:
	for line in tqdm(f, total=cnt):
		x=line.rstrip('\n')
		y=bip39(x)
		i=y+' 0\n'
		outfile.write(i)
		outfile.flush()

outfile.close()
