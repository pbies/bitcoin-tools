#!/usr/bin/env python3

from bsddb3 import db
import json
import os
import sys

for infile in os.listdir('.'):
	if os.path.isfile(infile) and infile[-4:]=='.dat':
		wallet_file_path=infile

		print(f'{infile}...', end='', flush=True)

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
			print(f"Error: {e}")
			continue

		wallet_db2 = db.DB()
		fn, ext = os.path.splitext(wallet_file_path)
		wallet_db2.open(f'{fn}-repaired{ext}', 'main', db.DB_BTREE, db.DB_CREATE)

		for k, v in data.items():
			wallet_db2.put(k, v)

		print('ok')

print()
print('\a', end='', file=sys.stderr)
