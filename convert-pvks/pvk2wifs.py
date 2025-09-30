#!/usr/bin/env python3

from functools import partial
from hdwallet import HDWallet
from hdwallet.symbols import BTC
import base58
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

i=input('Enter private key in hex (64 hex digits):')

i='0'*(64-len(i))+i

wif=pvk_to_wif2(i)
hdwallet=HDWallet(symbol=BTC)
hdwallet.from_private_key(private_key=i)

print(f'pvk: {i}')
print(f'WIF uncomp: {wif}')
print(f'WIF comp: {hdwallet.wif()}')
