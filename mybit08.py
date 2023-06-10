#!/usr/bin/env python3

# mybit build 220802a-220805a

import sys

if len(sys.argv[1:])<2:
	print(f"\nUsage: {sys.argv[0]} -option file/folder")
	print("\nOptions:")
	print("\n-w      show wallet info, provide path to wallet file")
	print("-b      show blockchain info, provide path to blockchain folder")
	sys.exit(0)

def create_env(db_dir):
	db_env = DBEnv(0)
	r = db_env.open(db_dir, (DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN|DB_THREAD|DB_RECOVER))
	return db_env

print("Importing bsddb3...", end="")
try:
	import bsddb3
	from bsddb3.db import *
except:
	print("error: no bsddb3; run: pip install bsddb3")
	sys.exit(1)
print("ok")
print("bsddb3 version "+bsddb3.__version__)
tmp=bsddb3.db
print("bsddb3 returns ",end="")
print(tmp.version())
print("bsddb3 full version: ",end="")
print(tmp.full_version())

opt=sys.argv[1]

if opt=="-w":
	print("Opening wallet...",end="")
	db_env = create_env('.')
	db = DB(db_env)
	DB_TYPEOPEN = DB_RDONLY
	flags = DB_THREAD | DB_TYPEOPEN
	try:
		r = db.open(sys.argv[2],"main",DB_BTREE, flags)
	except:
		print("error: bad wallet")
		sys.exit(1)
	print("ok")
	cur = db.cursor()
	rec = cur.first()
	while rec:
		print(rec)
		try:
			rec = cur.next()
		except:
			print("End of data")
			break
	db.close()
	sys.exit(0)

elif opt=="-b":
	print("Opening blockchain...",end="")

	sys.exit(0)

else:
	print("Error: unknown option")
	sys.exit(1)
