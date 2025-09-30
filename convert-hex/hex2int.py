#!/usr/bin/env python3

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]
f.close()

outfile = open("output.txt","w")
for x in content:
	outfile.write(str(int(x,16))+'\n')

outfile.close()
