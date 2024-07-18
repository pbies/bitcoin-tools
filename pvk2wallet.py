#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from pprint import pprint

hdwallet = HDWallet(symbol=BTC)

pvk=input('Enter private key without 0x: ')
hdwallet.from_private_key(private_key=pvk)
pprint(hdwallet.dumps())
