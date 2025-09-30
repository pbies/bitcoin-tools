#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

import bip32utils
import mnemonic

def bip39(mnemonic_words):
	mobj = mnemonic.Mnemonic("english")
	seed = mobj.to_seed(mnemonic_words)

	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
	bip32_child_key_obj = bip32_root_key_obj.ChildKey(
		84 + bip32utils.BIP32_HARDEN
	).ChildKey(
		2 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(0).ChildKey(0)

	return bip32_child_key_obj.WalletImportFormat()

if __name__ == '__main__':
	f=open("input.txt","r")
	o=open("output.txt","w")
	for l in f:
		l=l.strip()
		x=bip39(l)
		o.write(x+'\n')
