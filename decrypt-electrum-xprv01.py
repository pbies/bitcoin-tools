#!/usr/bin/env python3

from electrum.crypto import pw_decode

i=open('input.txt','r').read().splitlines()

for x in i:
	print( pw_decode(x, 'password', version=1) )
