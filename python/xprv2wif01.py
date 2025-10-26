#!/usr/bin/env python3

from bitcoinlib.keys import HDKey

i=open('input.txt','r').read().splitlines()
o=open('output.txt','w')

for x in i:
	y = HDKey(x)
	o.write(f'{x} {y.wif()}\n')
