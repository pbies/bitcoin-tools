#!/usr/bin/env python3

i=open("input.txt","r")
o=open("output.txt","w")

while l:=i.readline():
	if (len(l)==7) or (len(l)==8):
		o.write(l)
