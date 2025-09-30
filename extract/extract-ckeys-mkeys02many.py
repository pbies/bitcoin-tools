#!/usr/bin/env python3

# pip3 install pycryptodome bsddb3

import os
import bsddb3.db as bdb
import struct

def extract_keys(wallet_path):
	try:
		# Open the wallet.dat file
		db_env = bdb.DBEnv()
		db_env.open(os.path.dirname(wallet_path), bdb.DB_CREATE | bdb.DB_INIT_MPOOL)
		db = bdb.DB(db_env)
		db.open(wallet_path, "main", bdb.DB_BTREE, bdb.DB_RDONLY)

		mkey, ckeys = None, []

		for key, value in db.items():
			if key.startswith(b'\x04mkey'):
				mkey = value  # Extract master key
			elif key.startswith(b'\x04ckey'):
				ckeys.append(value)  # Extract crypted keys

		db.close()
		db_env.close()

		return {"mkey": mkey, "ckeys": ckeys}

	except Exception as e:
		print(f"Error: {e}", file=sys.stderr)
		return None

o=open('output.txt','w')

if __name__ == "__main__":
	for infile in os.listdir('.'):
		if os.path.isfile(infile) and infile[-4:]=='.dat':
			result = extract_keys(infile)

			if result:
				print(f"File: {infile}")
				o.write(f"{result['mkey'].hex()[2:]+'\n' if result['mkey'] else ''}")
				for ckey in result['ckeys']:
					o.write(f"{ckey.hex()[2:]+'\n'}")
			else:
				print(f"Failed to extract keys from '{infile}' file.")
