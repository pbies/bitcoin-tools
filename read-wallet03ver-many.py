#!/usr/bin/env python3

from bsddb3 import db
from pathlib import Path

files = Path('.').glob('*.dat')

for f in files:
	print(str(f)+':',end='')
	wallet_db = db.DB()
	wallet_db.open(str(f), 'main', db.DB_BTREE, db.DB_RDONLY)
	cursor = wallet_db.cursor()
	record = cursor.first()

	while record:
		try:
			t=record[0][1:].decode()
			if t == "version":
				#print(t,end='')
				print(record[1].hex())
		except:
			pass
		record = cursor.next()
