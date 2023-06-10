#!/usr/bin/env python3

import os
from bitcoin import *

a = open("pub.txt","r")
print('Loading public...')
b = a.readlines()
c = [x.rstrip('\n') for x in b]
ra = open("found-pub.txt","w")
rb = open("found-priv.txt","wb")

print('Public loaded.')
print('Searching...')

while True:
	#print('.',end='',flush=True)
	privkey=os.urandom(32)
	pubaddr = privtoaddr(privkey)
	#print(pubaddr)
	if pubaddr in c:
		print('!',end='',flush=True)
		ra.write(pubaddr+'\n')
		ra.flush()
		rb.write(privkey)
		rb.flush()
