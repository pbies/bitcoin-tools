#!/usr/bin/env python3

import bsddb3.db as bdb
import sys

def extract_wallet_info(wallet_path):
	wallet = bdb.DB()
	wallet.open(wallet_path, 'main', bdb.DB_BTREE, bdb.DB_RDONLY)

	cursor = wallet.cursor()
	entry = cursor.first()
	wallet_info = []

	while entry:
		key, value = entry
		wallet_info.append((key, value))
		entry = cursor.next()

	cursor.close()
	wallet.close()

	return wallet_info

wallet_path = sys.argv[1]
wallet_info = extract_wallet_info(wallet_path)

for key, value in wallet_info:
	print(f'Key: {key.hex()}')
	print(f'Value: {value.hex()}')
	print('---')

import sys
print('\a',end='',file=sys.stderr)
