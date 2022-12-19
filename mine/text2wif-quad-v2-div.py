#!/usr/bin/env python3

import base58
import hashlib
import sys

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('once.txt','w')
p = open('twice.txt','w')

for line in content:
	a=bytes(line,'utf-8')
	b=hashlib.sha256(a).digest()
	c=b.hex()
	d='80'+c
	f=bytes.fromhex(d)
	g=base58.b58encode_check(f)
	h=g+" 0 # "+line+"\n"
	o.write(h)

	i=hashlib.sha256(b).digest()
	j=i.hex()
	k='80'+j
	l=bytes.fromhex(k)
	m=base58.b58encode_check(l)
	n=m+" 0 # "+line+"\n"
	p.write(n)

	while len(a)<32:
		a=bytes([0])+a

	b=hashlib.sha256(a).digest()
	c=b.hex()
	d='80'+c
	f=bytes.fromhex(d)
	g=base58.b58encode_check(f)
	h=g+" 0 # "+line+"\n"
	o.write(h)

	i=hashlib.sha256(b).digest()
	j=i.hex()
	k='80'+j
	l=bytes.fromhex(k)
	m=base58.b58encode_check(l)
	n=m+" 0 # "+line+"\n"
	p.write(n)