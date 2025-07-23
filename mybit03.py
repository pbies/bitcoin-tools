#!/usr/bin/env python3

# mybit build 1

import sys

#print(f"Arguments count: {len(sys.argv[1:])}")
#for i, arg in enumerate(sys.argv[1:]):
#	print(f"Argument {i:>6} = {arg}")

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
	print("Error: no bsddb3; run: pip install bsddb3", file=sys.stderr)
	sys.exit(1)
print("loaded")

opt=sys.argv[1]

if opt=="-w":
	print("Opening wallet...",end="")
	
	sys.exit(0)
elif opt=="-b":
	print("Opening blockchain...",end="")

	sys.exit(0)
else:
	print("Error: unknown option")
	sys.exit(1)
