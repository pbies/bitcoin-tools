#!/usr/bin/env python3

import requests
import os

def get_balance(address):
	url = f'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}'
	response = requests.get(url)
	if response.status_code == 200:
		data = response.json()
		if 'result' in data and data['result'] != '':
			balance = int(data['result']) / 10**18  # Convert balance from wei to Ether
			return balance
		else:
			print(f"Balance information not found or invalid for address: {address}")
			return None
	else:
		print(f"Failed to retrieve balance for address: {address}. Status code: {response.status_code}")
		return None

def extract_ethereum_addresses(file_path):
	addresses = []
	with open(file_path, 'r') as file:
		for line in file:
			words = line.strip().split()
			for word in words:
				if len(word) == 42 and word.startswith('0x'):  # Ethereum address format check
					addresses.append(word)
	return addresses

def load_processed_addresses(log_file):
	if os.path.exists(log_file):
		with open(log_file, 'r') as f:
			return {line.strip() for line in f}
	return set()

def save_processed_address(log_file, address):
	with open(log_file, 'a') as f:
		f.write(f'{address}\n')

def save_valid_address(output_file, address, balance):
	with open(output_file, 'a') as f:
		f.write(f'Address: {address}\nBalance: {balance} Ether\n')

ETHERSCAN_API_KEY = '2EM2PYTD6MTQEPKCKHHP92V1BWZE5DYVJX'
input_file = 'input.txt'
output_file = 'output.txt'
log_file = 'log.txt'

# Load previously processed addresses to resume
processed_addresses = load_processed_addresses(log_file)
ethereum_addresses = extract_ethereum_addresses(input_file)

# Sort the addresses to ensure they are processed in numeric order
ethereum_addresses.sort()

for address in ethereum_addresses:
	if address in processed_addresses:
		print(f'Skipping already processed address: {address}')
		continue

	balance = get_balance(address)
	if balance is not None and balance > 0.0:
		save_valid_address(output_file, address, balance)
		print(f'Address: {address}\nBalance: {balance} Ether\n')
	else:
		print(f'Address: {address} has a balance of {balance} Ether or is invalid.')

	# Save the address to the log file after processing
	save_processed_address(log_file, address)
