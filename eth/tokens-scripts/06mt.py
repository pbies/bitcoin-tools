#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from web3 import Web3
import json
import os
from tqdm.contrib.concurrent import process_map
import time

# konfiguracja
ALCHEMY_KEY = ""
w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"))

# adres docelowy (twój "główny portfel")
DESTINATION = "0x..."

# ABI standardowego ERC20 (fragment wystarczający)
with open('abi.json','r') as f:
	ERC20_ABI = json.load(f)

# lista twoich portfeli i kluczy (uwaga: trzymaj bezpiecznie!)
s=open('output.txt','r').read().splitlines()

def transfer_all(pvk, wallet_addr, token_addr, amnt):
	acct = w3.eth.account.from_key(pvk)
	contract = w3.eth.contract(address=w3.to_checksum_address(token_addr), abi=ERC20_ABI)

	balance = contract.functions.balanceOf(wallet_addr).call()
	if balance == 0:
		print(f"{wallet_addr} -> {token_addr}: brak salda")
		return

	nonce = w3.eth.get_transaction_count(wallet_addr)
	tx = contract.functions.transfer(DESTINATION, balance).build_transaction({
		"from": wallet_addr,
		"nonce": nonce,
		"gas": 100000,
		"gasPrice": w3.to_wei("15", "gwei"),
	})

	signed = w3.eth.account.sign_transaction(tx, pvk)
	try:
		tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
		print(f"\a\nPrzesłano {balance} tokenów {token_addr} z {wallet_addr} -> {DESTINATION}, tx: {tx_hash.hex()}")
	except Exception as e:
		pass#print(f"Nie udało się: {e}")

def go(i):
	time.sleep(.25)
	i=i.split(',')
	pvk=i[1]
	wallet_addr=w3.to_checksum_address(i[0])
	token_addr=i[3]
	amnt=i[4]
	transfer_all(pvk, wallet_addr, token_addr, amnt)

def main():
	process_map(go, s, max_workers=2, chunksize=10)

if __name__ == "__main__":
	main()
