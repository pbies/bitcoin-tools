#!/usr/bin/env python3

print("mybit (C) 2022 Piotr Biesiada")
# mybit build 220802a

import sys

if len(sys.argv[1:])<2:
	print(f"\nUsage: {sys.argv[0]} -option file/folder")
	print("\nOptions:")
	print("\n-w      show wallet info, provide path to wallet file")
	print("-b      show blockchain info, provide path to blockchain folder")
	sys.exit(0)

print("Importing bsddb3...", end="")
try:
	import bsddb3
	from bsddb3 import *
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
	db = bsddb3.btopen(sys.argv[2],'r')
	print("ok")
	db_type="btree"
	db.set_location(b"main")
	rec = db.first()
	while rec:
		print(rec)
		try:
			rec = db.next()
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
