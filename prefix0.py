#!/usr/bin/env python3

i=open('input.txt','r')
o=open('output.txt','w')

for line in i:
	line='0'*(66-len(line))+line
	o.write(line)
