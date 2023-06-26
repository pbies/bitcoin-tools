#!/usr/bin/env python3

i=open("input.txt","rb")
o=open("output.txt","wb")
while (byte := i.read(1)):
	if (((byte>=b'\x20') and (byte<=b'\x7f')) or (byte==b'\x0a')):
		o.write(byte)
