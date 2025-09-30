#!/usr/bin/env python3

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

import pprint
import binascii
import mnemonic
import bip32utils

def bip39(mnemonic_words):
	mobj = mnemonic.Mnemonic("english")
	seed = mobj.to_seed(mnemonic_words)

	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
	bip32_child_key_obj = bip32_root_key_obj.ChildKey(
		44 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(0).ChildKey(0)

	return bip32_child_key_obj.WalletImportFormat()


if __name__ == '__main__':
	with open("input.txt","r") as f:
		lines = f.readlines()

	lines = [x.strip() for x in lines]

	with open("output.txt","w") as o:
		for line in lines:
			t=bip39(line)
			pprint.pprint(t)
			o.write(t+'\n')
