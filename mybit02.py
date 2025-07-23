#!/usr/bin/env python3

# mybit build 1

import sys

print(f"Arguments count: {len(sys.argv[1:])}")
#for i, arg in enumerate(sys.argv[1:]):
#	print(f"Argument {i:>6} = {arg}")

if len(sys.argv[1:])<2:
	print("\nUsage: mybit.py -option file/folder")
	print("\nOptions:")
	print("\n-r      show wallet info, provide path to wallet file")
	print("-b      show blockchain info, provide path to blockchain folder")
	sys.exit(0)

print("importing bsddb3...", end="")
try:
	import bsddb3
except:
	print("error: no bsddb3; run: pip install bsddb3", file=sys.stderr)
	sys.exit(1)
print("loaded")

opt=sys.argv[1]

if opt=="-r":
	print("Opening wallet...",end="")
elif opt=="-b":
	print("Opening blockchain...",end="")
