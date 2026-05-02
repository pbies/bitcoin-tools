#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys, base58, random
import itertools, math, time
from itertools import combinations

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.seeds import BIP39Seed

_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

class Timer:
	def __enter__(self):
		self.start = time.perf_counter()
	def __exit__(self, type, value, traceback):
		self.end = time.perf_counter()
		print(f"This took: {self.end - self.start: .5f} seconds")

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

targets=set()

def go(key_hex):
	_hdwallet.from_private_key(key_hex)
	t=_hdwallet.address('P2PKH')
	if t in targets:
		wif1 = pvk_to_wif2(key_hex)
		wif2 = _hdwallet.wif()
		line = f'{key_hex} {wif1} {wif2} {t}\n'
		with open('found.txt', 'a') as o:
			o.write(line)
			o.flush()

primes=set()

def gen():
	global primes
	for r in range(1, 9):
		i=itertools.product(primes, repeat=r)
		for j in i:
			k=math.prod(j)
			if k>=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140:
				continue
			yield hex(k)[2:].zfill(64)

def main():
	global primes, targets
	print('Loading targets...', flush=True)
	targets=set(open('input1.txt','r').read().splitlines())
	print('Loading primes...', flush=True)
	with Timer():
		primes_src=set(open('input2.txt','r').read().splitlines())
	print('Converting primes...', flush=True)
	with Timer():
		primes = set( int(x) for x in primes_src )

	print('Starting search...', flush=True)
	tmp=0
	for r in range(1, 6):
		tmp+=len(primes)**r
	t=tqdm(total=tmp)
	with Pool(cpu_count()//2) as pool:
		for res in pool.imap_unordered(go, gen()):
			t.update()

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
