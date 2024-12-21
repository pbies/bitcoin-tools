#!/usr/bin/env python3

from bsddb3 import db
import json
import os
import sys

if len(sys.argv) != 2:
	print(f"Usage: python {sys.argv[0]} <wallet_file_path>")
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

wallet_db2 = db.DB()
fn, ext = os.path.splitext(wallet_file_path)
wallet_db2.open(fn+'-repaired'+ext, 'main', db.DB_BTREE, db.DB_CREATE)

for k, v in data.items():
	wallet_db2.put(k, v)

print('\a', end='', file=sys.stderr)
