#!/usr/bin/env python3

import re

# Function to extract Ethereum addresses from a string
def extract_ethereum_addresses(text):
	pattern = r'0x[a-fA-F0-9]{40}'
	ethereum_addresses = re.findall(pattern, text)
	return ethereum_addresses

# Read from List.txt
with open('input.txt', 'r') as file:
	data = file.read()

# Extract Ethereum addresses
ethereum_addresses = extract_ethereum_addresses(data)

# Write Ethereum addresses to list.txt
with open('output.txt', 'w') as file:
	for address in ethereum_addresses:
		file.write(address + '\n')
