#!/usr/bin/env python3

from tqdm import tqdm
from multiprocessing import Pool, Lock, Manager

import os, sys, time, datetime

os.system('cls||clear')

i = open('input.txt','rb').read().splitlines()

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open('errors.txt', 'a') as log_file:
		log_file.write(f'{timestamp} {message}\n')
	#print(f'{timestamp} {message}', flush=True)

if os.path.exists("output.txt"):
	os.remove("output.txt")

th=16

def go(x):
	try:
		y=x.decode()[:-1]
		with open('output.txt','a') as o:
			o.write(f"{y}\n")
	except:
		log('Error with: {y}')

with Pool(processes=th) as pool:
	list(tqdm(pool.imap_unordered(go, i, chunksize=th*4), total=len(i)))

print('\aDone.', file=sys.stderr)
