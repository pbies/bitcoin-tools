#!/usr/bin/env python3

from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip39MnemonicGenerator, Bip39Languages, Bip39MnemonicValidator
import binascii
from tqdm import tqdm

def generate_keys(seed_bytes, num_keys):
	bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)

	keys = []

	for i in range(num_keys):
		bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)

		private_key_hex = bip44_acc_ctx.PrivateKey().Raw().ToHex()
		private_key_wif = bip44_acc_ctx.PrivateKey().ToWif()
		public_key = bip44_acc_ctx.PublicKey().RawCompressed().ToHex()
		
		keys.append({
			'index': i,
			'private_key_hex': private_key_hex,
			'private_key_wif': private_key_wif,
			'public_key': public_key,
			'address': bip44_acc_ctx.PublicKey().ToAddress()
		})

	return keys

o=open('mnemos.txt','r').read().splitlines()

for i in tqdm(o):
	if not Bip39MnemonicValidator().IsValid(i):
		continue
	print(f"Mnemonic: {i}")

	seed_bytes = Bip39SeedGenerator(i).Generate()

	keys = generate_keys(seed_bytes, 100)

	for key in keys:
		print(f"Index: {key['index']}, Private Key hex: {key['private_key_hex']}, Private Key WIF: {key['private_key_wif']}, Public Key: {key['public_key']}, Address: {key['address']}")

import sys
print('\a',end='',file=sys.stderr)
