#!/usr/bin/env python3
data=[]
for a in range(256):
	for b in range(256):
		data.append(a)
		data.append(b)
		data.append(10)
bytes = bytearray(data)
with open("output.txt", "wb") as f:
	f.write(bytes)
	f.close()
