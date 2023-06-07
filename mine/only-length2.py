#!/usr/bin/env python3

from tqdm import tqdm

cnt=sum(1 for line in open("input.txt", 'r'))

with open('input.txt') as i:
	with open('output.txt','w') as o:
		for line in tqdm(i, total=cnt, unit="k"):
			word = line.strip()
			if len(word) == 64:
				o.write(word+'\n')
