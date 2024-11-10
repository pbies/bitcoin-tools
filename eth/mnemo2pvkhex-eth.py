#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

import base58
import binascii
import bip32utils
import mnemonic
import pprint

def bip39(mnemonic_words):
	mobj = mnemonic.Mnemonic("english")
	seed = mobj.to_seed(mnemonic_words)

	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
	bip32_child_key_obj = bip32_root_key_obj.ChildKey(
		44 + bip32utils.BIP32_HARDEN
	).ChildKey(
		60 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(0).ChildKey(0)

	return bip32_child_key_obj.WalletImportFormat()

def wif_to_privatekey(s):
	b = base58.b58decode_check(s)
	return b

if __name__ == '__main__':
	f=open("input.txt","r")
	o=open("output.txt","w")
	for l in f:
		l=l.strip()
		x=bip39(l)
		y=wif_to_privatekey(x)
		o.write(y[1:-1].hex()+'\n')
