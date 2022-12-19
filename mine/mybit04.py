#!/usr/bin/env python3

print("mybit (C) 2022 Piotr Biesiada")
# mybit build 220802a

import sys

if len(sys.argv[1:])<2:
	print("\nUsage: mybit.py -option file/folder")
	print("\nOptions:")
	print("\n-w      show wallet info, provide path to wallet file")
	print("-b      show blockchain info, provide path to blockchain folder")
	sys.exit(0)

print("Importing bsddb3...", end="")
try:
	import bsddb3
except:
	print("error: no bsddb3; run: pip install bsddb3")
	sys.exit(1)
print("loaded")

opt=sys.argv[1]

if opt=="-w":
	print("Opening wallet...",end="")
	w = bsddb3.btopen(sys.argv[2],"r")
	print("ok")
	
	sys.exit(0)
elif opt=="-b":
	print("Opening blockchain...",end="")

	sys.exit(0)
else:
	print("Error: unknown option")
	sys.exit(1)
