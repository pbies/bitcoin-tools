#!/usr/bin/env python3

i=open('input.txt','r')
o=open('output.txt','w')

for l in i:
	l=l.rstrip('\n')
	n=l.split(',')
	o.write(n[1]+','+n[0]+','+n[3]+'\n')
