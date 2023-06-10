#!/usr/bin/env python3

# many base58check to hex

import base58
import hashlib
import sys

def b58(str):
	return base58.b58decode_check(str)

def main():
	with open("input.txt") as f:
		content = f.readlines()

	content = [x.strip() for x in content]

	o = open('output.txt','w')

	for line in content:
		o.write(b58(line).hex() + "\n")

if __name__ == '__main__':
	main()
