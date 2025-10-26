#!/usr/bin/env python3

from bitcoinlib.keys import HDKey
from bip32 import BIP32
import base58
import hashlib

i=set(open('input.txt','r').read().splitlines())
o=open('output.txt','w')

def xprv_to_wif(xprv: str, testnet=False) -> str:
	bip32 = BIP32.from_xpriv(xprv)
	privkey_bytes = bip32.get_privkey_from_path([])  # root key

	prefix = b'\x80' if not testnet else b'\xef'
	extended_key = prefix + privkey_bytes + b'\x01'  # add compressed flag
	checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
	wif = base58.b58encode(extended_key + checksum)
	return wif.decode()

for x in i:
	o.write(f'{x} {xprv_to_wif(x)}\n')
