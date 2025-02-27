#!/usr/bin/env python3

from bsddb3 import db
import json
import os
import sys

if len(sys.argv) != 2:
	print(f"Usage: python3 {sys.argv[0]} <wallet_file_path>")
	sys.exit(1)

wallet_file_path = sys.argv[1]

for g in ['main','key','defaultkey','name','tx','pool','version','cscript','bestblock','walletsettings','minversion','watchonly','hdseed']:

	print(g+' ', end='', flush=True)

	data=[]

	try:
		wallet_db = db.DB()
		wallet_db.open(wallet_file_path, g, db.DB_BTREE, db.DB_RDONLY)
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
		print("error")
		continue

	wallet_db2 = db.DB()
	fn, ext = os.path.splitext(wallet_file_path)
	wallet_db2.open(fn+'-repaired'+ext, g, db.DB_BTREE, db.DB_CREATE)

	for k, v in data.items():
		wallet_db2.put(k, v)

	print('ok')

print()
print('\a', end='', file=sys.stderr)
