#!/usr/bin/env python3

import os
folder = '.'
s='5JdeC9P7Pbd1uGdFVEsJ41EkEnADbbHGq6p1BwFxm6txNBsQnsw'

for filename in os.listdir(folder):
	f = os.path.join(folder, filename)
	if os.path.isfile(f):
		print('Processing '+f)
		i=open(f,'r')
		o=open(f+'.new','w')
		for line in i:
			if s in line:
				continue
			o.write(line)
		i.close()
		o.close()
		os.rename(f+'.new',f)
