#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

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

	# return {
	#	 'mnemonic_words': mnemonic_words,
	#	 'bip32_root_key': bip32_root_key_obj.ExtendedKey(),
	#	 'bip32_extended_private_key': bip32_child_key_obj.ExtendedKey(),
	#	 'bip32_derivation_path': "m/44'/0'/0'/0",
	#	 'bip32_derivation_addr': bip32_child_key_obj.Address(),
	#	 'coin': 'BTC'
	# }

	return bip32_child_key_obj.WalletImportFormat()# {
		# 'mnemonic_words': mnemonic_words,
		# 'bip32_root_key': bip32_root_key_obj.ExtendedKey(),
		# 'bip32_extended_private_key': bip32_child_key_obj.ExtendedKey(),
		# 'path': "m/44'/0'/0'/0",
		# 'addr': bip32_child_key_obj.Address(),
		# 'publickey': binascii.hexlify(bip32_child_key_obj.PublicKey()).decode(),
		# 'privatekey': bip32_child_key_obj.WalletImportFormat(),
		# 'coin': 'BTC'
	# }


if __name__ == '__main__':
	with open("input.txt","r") as f:
		lines = f.readlines()

	lines = [x.strip() for x in lines]

	with open("output.txt","w") as o:
		for line in lines:
			t=bip39(line)
			#pprint.pprint(t)
			o.write(t+'\n')
