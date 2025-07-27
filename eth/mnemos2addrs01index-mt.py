#!/usr/bin/env python3

from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from eth_account.hdaccount import HDPath
from tqdm import tqdm
from multiprocessing import Pool, Lock, Manager

import os, sys, time, datetime

# RPC provider (use your own endpoint)
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_API_KEY"))
w3.eth.account.enable_unaudited_hdwallet_features()

os.system('cls||clear')

# Example: list of mnemonics
print('Reading...', flush=True)
mnemonics = open('input.txt','r').read().splitlines()

# Check N accounts per mnemonic
accounts_per_mnemonic = 5
derivation_path_format = "m/44'/60'/0'/0/{}"

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open('errors.txt', 'a') as log_file:
		log_file.write(f'{timestamp} {message}\n')
	#print(f'{timestamp} {message}', flush=True)

if os.path.exists("output.txt"):
	os.remove("output.txt")

th=16

def go(mnemonic):
	for i in range(accounts_per_mnemonic):
		path = derivation_path_format.format(i)
		try:
			acct = Account.from_mnemonic(mnemonic, account_path=path)
		except Exception as e:
			log(f'Error with {mnemonic} - {e}')
			continue
		address = acct.address
		with open('output.txt','a') as o:
			o.write(f"{mnemonic},{i},{address}\n")

print('Writing...', flush=True)

with Pool(processes=th) as pool:
	list(tqdm(pool.imap_unordered(go, mnemonics, chunksize=th*4), total=len(mnemonics)))

print('\aDone.', end='', file=sys.stderr)
