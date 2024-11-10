#!/usr/bin/env python3

from web3.auto import w3

w3.eth.account.enable_unaudited_hdwallet_features()
acc = w3.eth.account.from_mnemonic('abuse whale taste tag marine run drop marble champion august secret drama')
print(acc._private_key.hex())
