#!/usr/bin/env python3

print('Loading source...',end='',flush=True)
i1=open('blockchair_ethereum_addresses_latest.tsv','r')
i2=i1.read().splitlines()
i3=[line.split('\t') for line in i2]
ic=len(i3)
print('done',flush=True)

print('Loading target...',end='',flush=True)
j1=open('input.txt','r')
j2=j1.read().splitlines()
j3=[line.lower()[2:] for line in j2]
jc=len(j3)
print('done',flush=True)

c=0

print('Main work...',flush=True)
for x in j3:
	if c%1000==0:
		print(c,end='\r')
	for y in i3:
		if x==y[0]:
			print(y)
	c=c+1
