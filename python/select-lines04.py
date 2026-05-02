#!/usr/bin/env python3

import sys

i=open('output.txt','r')
o=open('output3.txt','w')

while True:
	x=1
	q=False
	for j in range(11):
		l=i.readline()
		if not l:
			q=True
			break
		if x==1:
			x+=1
			continue
		o.write(l)
	if q:
		break

print('\a', end='', file=sys.stderr)
