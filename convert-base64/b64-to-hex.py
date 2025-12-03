#!/usr/bin/env python3

import base64
import sys

def main():

	in_path = open('input.txt','r')
	open('output.txt','w').close()

	for line in in_path.readlines():
		byt=base64.b64decode(line)
		h=byt.hex()
		with open('output.txt','a') as o:
			o.write(h+'\n')

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
