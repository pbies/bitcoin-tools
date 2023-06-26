#!/usr/bin/env python3

from bitcoin import *

a=open("search-for.txt")
b=a.readlines()
c = [x.strip() for x in b]

d=open("search-in.txt","rb")

f=open("output.txt","w")

i=1

for e in d:
	print(i,end='')
	print('\r',end='')
	e=e.strip()
	try:
		pub=privtoaddr(e)
		if pub in c:
			print('\n'+e+'\a\n')
			f.write(e+'\n')
			f.flush()
	except:
		continue
	i=i+1
