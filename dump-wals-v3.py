#!/usr/bin/env python3

import bsddb3.db as bdb
import os
import sys
from pathlib import Path

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

files = Path('.').glob('*.dat')

for f in files:
	#print(f)
	wallet_path = str(f)
	try:
		wallet_info = extract_wallet_info(wallet_path)
	except:
		print('Error occured!')
		continue

	for key, value in wallet_info:
		print(f'{key.hex()}')
		print(f'{value.hex()}')

print('\a',end='',file=sys.stderr)
