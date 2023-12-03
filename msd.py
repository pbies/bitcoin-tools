#!/usr/bin/env python3

def msd(i):
	while i>=10:
		i=int(i/10)
	return i

print(msd(123))
print(msd(3210))
