#!/usr/bin/env python3

import bip32utils

xprv = 'your_xprv_here'
root_key = bip32utils.BIP32Key.fromExtendedKey(xprv)
child_key = root_key.ChildKey(0).ChildKey(0)
address = child_key.Address()
print(f"The Bitcoin address for the given xprv is: {address}")
