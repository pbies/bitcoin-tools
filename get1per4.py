#!/usr/bin/env python3

infile=open('result.txt','r')
outfile=open('result2.txt','w')

while True:
	l=infile.readline()
	if l:
		outfile.write(l)
		t=infile.readline()
		t=infile.readline()
		t=infile.readline()
		outfile.flush()
	else:
		break
