#!/usr/bin/env python3

from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from eth_account.hdaccount import HDPath
from tqdm import tqdm

import os, sys, time, datetime

# RPC provider (use your own endpoint)
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/"))
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

print('Writing...', flush=True)
for mnemonic in tqdm(mnemonics):
	with open('output.txt','a') as o:
		o.write(f"\n🔑 Mnemonic: {mnemonic}\n")
	for i in range(accounts_per_mnemonic):
		path = derivation_path_format.format(i)
		try:
			acct = Account.from_mnemonic(mnemonic, account_path=path)
		except Exception as e:
			log(f'Error with {mnemonic} - {e}')
			continue
		address = acct.address
		balance=0
		try:
			balance = w3.eth.get_balance(address)
		except:
			try:
				time.sleep(2)
				balance = w3.eth.get_balance(address)
			except:
				time.sleep(5)
				balance = w3.eth.get_balance(address)
		eth_balance = w3.from_wei(balance, 'ether')
		with open('output.txt','a') as o:
			o.write(f"Address {i}: {address} | Balance: {eth_balance} ETH\n")

print('\aDone.', file=sys.stderr)
