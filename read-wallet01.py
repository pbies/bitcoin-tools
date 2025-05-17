#!/usr/bin/env python3

from bsddb3 import db

wallet_db = db.DB()
wallet_db.open("wallet.dat", 'main', db.DB_BTREE, db.DB_RDONLY)
cursor = wallet_db.cursor()
record = cursor.first()

while record:
	try:
		print(record[0].decode(),end='')  # Shows raw key-value pairs (encrypted)
	except:
		pass
	try:
		print('='+record[1].decode())  # Shows raw key-value pairs (encrypted)
	except:
		pass
	record = cursor.next()
