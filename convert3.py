#!/usr/bin/env python3

i=open('input.txt','r')
o=open('output.txt','w')

for l in i:
	l=l.strip()
	if l[-66:-64]!='0x':
		l=l[:-64]+'0x'+l[-64:]
		print(l)
	else:
		print(l)

