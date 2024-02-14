#!/usr/bin/env python3

# pip3 install git+https://github.com/mcdallas/cryptotools.git@master#egg=cryptotools
# pip3 install p_tqdm
# pip3 install requests

from cryptotools.BTC import PrivateKey, send
from p_tqdm import p_map
import hashlib
import random
import sys
import requests

start=0x20000000000000000
end=0x3ffffffffffffffff
u=1024*1024*10 # range +-
right='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'

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
	a = key.to_public().to_address('P2PKH', compressed=True)
	if a==right:
		print('Found!')
		print(ra)
		print(hex(ra))
		print('WIF: '+getWif(byt))
		print('\a',flush=True)
		try:
			requests.get('https://your.domain.com/WALLET:'+getWif(byt))
		except:
			pass
		with open('found.txt','a') as f:
			f.write(str(ra))
			f.write('\n')
			f.write(hex(ra))
			f.write('\n')
			f.write('WIF: '+getWif(byt)+'\n')
			f.flush()
		sys.exit(0)
	return

def growing_range(mid,x): # x = range +-
	start=mid-x
	end=mid+x
	rng = [0] * (x*2-1)
	rng[::2], rng[1::2] = range(mid, end), range(mid-1, start, -1)
	return rng

print('target: '+right, flush=True)

while True:
	ra=2890446789805576192
	#rb=ra+u
	print(f'\rfrom: {hex(ra-u)} to: {hex(ra+u)} range: {hex(u)}={u}',flush=True)
	p_map(go, list(growing_range(ra, u)), num_cpus=8)
