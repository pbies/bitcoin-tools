#!/usr/bin/env python3

# pip3 install git+https://github.com/mcdallas/cryptotools.git@master#egg=cryptotools
# pip3 install p_tqdm
# pip3 install requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptotools.BTC import PrivateKey, send
from multiprocessing import Pool
from multiprocessing.pool import Pool
from p_tqdm import p_map
from time import sleep, perf_counter
from tqdm import *
from tqdm.contrib.concurrent import process_map
import hashlib
import random
import requests
import sys
import time
import tqdm

u=1024 # range +-

def int_to_bytes3(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def getWif(privkey):
	wif = b"\x80" + privkey
	wif = b58(wif + sha256(sha256(wif))[:4])
	return wif

def b58(data):
	B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
	if data[0] == 0:
		return "1" + b58(data[1:])
	x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
	ret = ""
	while x > 0:
		ret = B58[x % 58] + ret
		x = x // 58
	return ret

def sha256(data):
	digest = hashlib.new("sha256")
	digest.update(data)
	return digest.digest()

def go(ra):
	byt=int_to_bytes3(int(ra),32)
	key = PrivateKey.from_hex(byt.hex())
	pvk = getWif(byt)
	a = key.to_public().to_address('P2PKH', compressed=True)
	o.write(pvk+' - '+a+'\n')
	o.flush()
	return

def growing_range(mid,x): # x = range +-
	start=mid-x
	end=mid+x
	rng = [0] * (x*2-1)
	rng[::2], rng[1::2] = range(mid, end), range(mid-1, start, -1)
	return rng

o=open('output.txt','a')
o.write('start\n')
o.flush()

ra=int(2890446789805576192-(u/2))
r=list(growing_range(ra, u))
l=len(r)

# 01

print('01', flush=True)
start_time = perf_counter()
p_map(go, r)
end_time = perf_counter()
print(f'It took {end_time - start_time:0.6f} second(s) to complete.')

# 02

print('02', flush=True)
start_time = perf_counter()
ex=ThreadPoolExecutor(max_workers=2)
for i in r:
	ex.submit(go, i)
end_time = perf_counter()
print(f'It took {end_time - start_time:0.6f} second(s) to complete.')

# 03

#print('03', flush=True)
#start_time = perf_counter()
#with Pool(2) as p:
#	r = list(tqdm.tqdm(p.imap_unordered(go, r, chunksize=1000), total=l))
#end_time = perf_counter()
#print(f'It took {end_time - start_time:0.6f} second(s) to complete.')

# 04

#print('04', flush=True)
#start_time = perf_counter()
#r = process_map(go, r, max_workers=2, chunksize=1)
#end_time = perf_counter()
#print(f'It took {end_time - start_time:0.6f} second(s) to complete.')

# 05

#print('05', flush=True)
#start_time = perf_counter()
#pool = Pool(2)
#pool.map(go, r, chunksize=1)
#pool.close()
#pool.join()
#end_time = perf_counter()
#print(f'It took {end_time - start_time:0.6f} second(s) to complete.')

# 06

print('06', flush=True)
start_time = perf_counter()
with Pool(processes=2) as p:
	with tqdm.tqdm(total=l) as pbar:
		for _ in p.imap_unordered(go, r, chunksize=1000):
			pbar.update()
end_time = perf_counter()
print(f'It took {end_time - start_time:0.6f} second(s) to complete.')

o.flush()
o.close()
