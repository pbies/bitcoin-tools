#!/usr/bin/env python3

from mnemonic import Mnemonic
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import base58
import binascii

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/-ixFHz8NzHoGk2OOYc3EPLH9BxZpHfQ_"

w3 = Web3(Web3.HTTPProvider(alchemy_url))

i=open('input.txt','r')
o=open('output.txt','a')

lines=i.readlines()
ref = [x.strip() for x in lines]
ref = [w3.to_checksum_address(x) for x in ref]

for i in ref:
	o.write(i+'\n')

o.flush()
