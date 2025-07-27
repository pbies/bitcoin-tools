#!/usr/bin/env python3

# even with 2 threads it is too fast

from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from eth_account.hdaccount import HDPath
from tqdm import tqdm
from multiprocessing import Pool, Lock, Manager

import os, sys, time

# RPC provider (use your own endpoint)
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/"))
w3.eth.account.enable_unaudited_hdwallet_features()

# Example: list of mnemonics
print('Reading...', flush=True)
mnemonics = open('input.txt','r').read().splitlines()

def go(mnemonic):
	time.sleep(.1)
	accounts_per_mnemonic = 5
	derivation_path_format = "m/44'/60'/0'/0/{}"
	w=[]
	w.append(f"\n🔑 Mnemonic: {mnemonic}\n")
	for i in range(accounts_per_mnemonic):
		path = derivation_path_format.format(i)
		acct = Account.from_mnemonic(mnemonic, account_path=path)
		address = acct.address
		balance = w3.eth.get_balance(address)
		eth_balance = w3.from_wei(balance, 'ether')
		w.append(f"Address {i}: {address} | Balance: {eth_balance} ETH\n")
	with open('output.txt','a') as o:
		o.writelines(w)

th=2

print('Writing...', flush=True)

with Pool(processes=th) as pool:
	list(tqdm(pool.imap_unordered(go, mnemonics, chunksize=th*4), total=len(mnemonics)))

print('\aDone.', file=sys.stderr)
