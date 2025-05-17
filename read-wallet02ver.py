#!/usr/bin/env python3

from bsddb3 import db

wallet_db = db.DB()
wallet_db.open("wallet.dat", 'main', db.DB_BTREE, db.DB_RDONLY)
cursor = wallet_db.cursor()
record = cursor.first()

while record:
	try:
		t=record[0][1:].decode()
		if t == "version":
			print(t,end='')
			print('='+record[1].hex())
	except:
		pass
	record = cursor.next()
