#!/usr/bin/env python3

from array import array

print('Loading source...',flush=True)
i1=open('blockchair_ethereum_addresses_latest.tsv','r')
print('Stage 1 - read')
i2=i1.read().splitlines()
print('Stage 2 - split')
i3=[line.split('\t') for line in i2]
i4=[line[0] for line in i3]
ic=len(i3)
print('done',flush=True)

print('Loading target...',flush=True)
j1=open('input.txt','r')
print('Stage 1 - read')
j2=j1.read().splitlines()
print('Stage 2 - lower')
j3=[line.lower()[2:] for line in j2]
jc=len(j3)
print('done',flush=True)

c=0

print('Main work...',flush=True)
for x in j3:
	if c%1000==0:
		print(str(c)+'/'+str(jc),end='\r')
	if x in i4:
		idx=i4.index(x)
		print(i3[idx])
		xs=str(i3[idx])
		o=open('found.txt','a')
		o.write(xs)
		o.write('\n')
		o.flush()
		o.close()
	c=c+1

print('End of program')
