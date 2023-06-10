#!/usr/bin/env python3

i=open("input.txt","rb")
o=open("output.txt","w")
while True:
	pb=i.read(32)
	if len(pb) < 32:
		i.close()
		o.close()
		exit()
	ph=pb.hex()
	o.write(ph+'\n')
