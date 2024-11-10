#!/usr/bin/env python3

i=open('input.txt','r')

f = i.readlines()
f = [line.strip() for line in f]
f = [line.split() for line in f]
o=[]
for x in f:
	x.reverse()
	o.append(x)
f = [' '.join(line) for line in o]
p=open('output.txt','w')
for z in f:
	p.write(z+'\n')
