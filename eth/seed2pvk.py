#!/usr/bin/env python3

from mnemonic import Mnemonic
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import base58
import binascii
from tqdm import tqdm

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

w3 = Web3(Web3.HTTPProvider(alchemy_url))

mnemonic=Mnemonic("english")

xprv = mnemonic.to_hd_master_key(binascii.unhexlify('03049296dc75bad0fce03765126586077b0dce5c8ddeb1ec185f3c4cf2b6fd7c8feda311f8696c167dbacdc77970314bf83ffe6ad49f36381a9ab396184ce90f'))
pvk = base58.b58decode_check(xprv)[-32:]
print('0x'+pvk.hex())

xprv = mnemonic.to_hd_master_key(binascii.unhexlify('0805a279978c04c235648a08f9615eb0bf00ddf8f4fa75bc1d9ab164563985c4d48a0b583f2299bf5d9cfe70404e0b1e28e32b74858171e5748b39e448cd9cd0'))
pvk = base58.b58decode_check(xprv)[-32:]
print('0x'+pvk.hex())
