#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from web3 import Web3
import json
import os

# konfiguracja
ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY")
w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"))

# adres docelowy (twój "główny portfel")
DESTINATION = "0xYourTargetAddress"

# ABI standardowego ERC20 (fragment wystarczający)
ERC20_ABI = json.loads('[{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}]')

# lista twoich portfeli i kluczy (uwaga: trzymaj bezpiecznie!)
WALLETS = [
	{"address": "0xWallet1", "private": "0xPrivateKey1"},
	{"address": "0xWallet2", "private": "0xPrivateKey2"},
]

# kontrakty tokenów do przeniesienia
TOKENS = [
	"0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
	"0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
]

def transfer_all(wallet, token_addr):
	acct = w3.eth.account.from_key(wallet["private"])
	contract = w3.eth.contract(address=w3.to_checksum_address(token_addr), abi=ERC20_ABI)

	balance = contract.functions.balanceOf(wallet["address"]).call()
	if balance == 0:
		print(f"{wallet['address']} -> {token_addr}: brak salda")
		return

	nonce = w3.eth.get_transaction_count(wallet["address"])
	tx = contract.functions.transfer(DESTINATION, balance).build_transaction({
		"from": wallet["address"],
		"nonce": nonce,
		"gas": 100000,
		"gasPrice": w3.to_wei("15", "gwei"),
	})

	signed = w3.eth.account.sign_transaction(tx, wallet["private"])
	tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
	print(f"Przesłano {balance} tokenów {token_addr} z {wallet['address']} -> {DESTINATION}, tx: {tx_hash.hex()}")

def main():
	for wallet in WALLETS:
		for token in TOKENS:
			transfer_all(wallet, token)

if __name__ == "__main__":
	main()
