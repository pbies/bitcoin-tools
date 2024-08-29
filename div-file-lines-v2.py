#!/usr/bin/env python3

import sys
import math

fn=sys.argv[1]
div=int(sys.argv[2])

inp=open(fn,'r').read().splitlines()
cnt=len(inp)
lines=math.ceil(cnt/div)

print('all lines: '+str(cnt))
print('lines per part: '+str(lines))

for i in range(0,div):
	start=i*lines
	end=i*lines+lines
	if i==div-1:
		end=cnt
	out=open(fn+'.'+str(i+1),'w')
	for j in range(start,end):
		out.write(inp[j]+'\n')
	out.flush()
	out.close()
	print('Part written: '+str(i+1))

print('\a',end='',file=sys.stderr)
