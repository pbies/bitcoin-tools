#!/usr/bin/env python3
import hashlib
import sys
import pybip38 # pip install pybip38
from tqdm import tqdm
from subprocess import check_output
# Note: The pybip38 is limited to Bitcoin (only) BIP38 encoded keys, NOT other alt-coins that use BIP38. Probably based on validation performed by that library.

# Example BIP38 Key. Password = test
BIP38 = '6PnQmAyBky9ZXJyZBv9QSGRUXkKh9HfnVsZWPn4YtcwoKy5vufUgfA3Ld7'

cnt=int(check_output(["wc", "-l", "passwords.txt"]).split()[0])

for line in tqdm(open('passwords.txt','r',encoding='utf-8'), total=cnt, unit=" lines"):
	pw = str(line.strip())
	#print("# Trying password: %s" % pw)
	if pybip38.bip38decrypt(pw, BIP38) != False:
		print("\n## KEY FOUND: %s\a\n" % pw)
		sys.exit(0)

print("\n## Password NOT found :-(\a\n")
