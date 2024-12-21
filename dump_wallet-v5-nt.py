#!/usr/bin/env python3

from bsddb3 import db
import json
import os
import sys

if len(sys.argv) != 2:
	print("Usage: python dump_wallet.py <wallet_file_path>")
	sys.exit(1)

wallet_file_path = sys.argv[1]

data=[]

try:
	wallet_db = db.DB()
	wallet_db.open(wallet_file_path, 'main', db.DB_BTREE, db.DB_RDONLY)
	cursor = wallet_db.cursor()
	data = {}

	while True:
		record = cursor.next()
		if record is None:
			break

		key, value = record

		data[key] = value

	cursor.close()
	wallet_db.close()

except Exception as e:
	print(f"Failed to load wallet file: {e}")
	sys.exit(1)

for k, v in data.items():
	t='unknown'
	match k.hex()[0:2]:
		case '02':
			t='KEY'
		case '03':
			t='WKEY'
		case '05':
			t='NAME'
		case '07':
			t='POOL'
		case '09':
			t='ACC'
		case '0a':
			t='ACENTRY'
		case '0c':
			t='CSCRIPT'
		case '12':
			t='WTX'
	print(f'type: {t}\nkey: {k.hex()}\nvalue: {v.hex()}\n')

print('\a', end='', file=sys.stderr)
"""
0x02: KEY - Private key entries (in very old or unencrypted wallets, these store the pubkey and corresponding private key).

0x03: WKEY - An older, now-deprecated record type related to wallet keys. It was used in very early wallet versions and isn’t typically seen in modern wallets.

0x05: NAME - Address book entries (the "label" or "name" associated with a particular Bitcoin address).

0x07: POOL - Keypool entries (pre-generated addresses/keys waiting to be used).

0x09: ACC - Account records (from older wallet versions that supported accounts, now deprecated).

0x0a: ACENTRY - Account entry records, detailing transactions or balances associated with named accounts (also deprecated).

0x0c: CSCRIPT - Storing redeem scripts (used for P2SH addresses or other special script conditions).

0x12: WTX (Transaction) - Full transaction records relevant to the wallet’s balance and history.

Grouping by Record Type:

Keys (private keys): Look for 0x02 (and sometimes 0x03 in very old wallets).

Address-related metadata: 0x05 (NAME) stores address labels.

Keypool and Account Info: 0x07 (POOL) and 0x09/0x0a (ACC/ACENTRY) for pre-HD, account-based workflows.

Scripts: 0x0c (CSCRIPT) for redeem scripts.

Transactions: 0x12 (WTX) for recorded wallet transactions.
"""
