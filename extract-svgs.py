#!/usr/bin/env python3

import sys, os, re

os.system('cls||clear')

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

a=open('input.txt','r')
b=a.read()
d=find_all_matches('<svg xmlns=.*</svg>', b)
n=1
for i in d:
	c=open(f'result{str(n)}.svg','w')
	c.write(i+'\n')
	c.close()
	n=n+1

print('\a', end='', file=sys.stderr)
