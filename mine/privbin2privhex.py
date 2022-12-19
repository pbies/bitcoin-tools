#!/usr/bin/env python3

i=open("input.txt","rb")
o=open("output.txt","w")
pb=i.read(32)
ph=pb.hex()
o.write(ph+'\n')
i.close()
o.close()
