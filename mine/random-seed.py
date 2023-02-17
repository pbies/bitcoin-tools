#!/usr/bin/env python3
import random

lines = open('seed.txt').read().splitlines()
for i in range(12):
	myline =random.choice(lines)
	print(myline+' ',end='')

# may be incorrect, you need to check if checksum is valid
