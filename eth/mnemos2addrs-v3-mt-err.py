#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
from web3.auto import w3
import binascii
import mnemonic
import sys

i = open('input.txt','r').read().splitlines()

open('output.txt','w').close()
open('errors.txt','w').close()

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

def go(i):
	try:
		acc = w3.eth.account.from_mnemonic(i)
	except:
		with open('errors.txt','a') as e:
			e.write(f'Bad mnemo: {i}\n')
		return
	address = w3.to_checksum_address(acc.address)
	with open('output.txt','a') as o:
		o.write(f'{address} {i}\n')

process_map(go, i, max_workers=24, chunksize=1000)

print('\a', end='', file=sys.stderr)
