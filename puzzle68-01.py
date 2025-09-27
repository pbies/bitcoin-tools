#!/usr/bin/env python3

from multiprocessing import Pool
import datetime
import ecdsa
import hashlib
import os
import random
import sys
import time

def sha256(data):
	return hashlib.sha256(data).digest()

def ripemd160(x):
	return hashlib.new("ripemd160", x).digest()

def log(t):
	d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print(f'{d} {t}', flush=True, end='')
	l=open('log.txt','a')
	l.write(f'{d} {str(t)}')
	l.flush()
	l.close()

class Point:
	def __init__(self,
		x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
		y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
		p=2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1):
		self.x = x
		self.y = y
		self.p = p

	def __add__(self, other):
		return self.__radd__(other)

	def __mul__(self, other):
		return self.__rmul__(other)

	def __rmul__(self, other):
		n = self
		q = None

		for i in range(256):
			if other & (1 << i):
				q = q + n
			n = n + n

		return q

	def __radd__(self, other):
		if other is None:
			return self
		x1 = other.x
		y1 = other.y
		x2 = self.x
		y2 = self.y
		p = self.p

		if self == other:
			l = pow(2 * y2 % p, p-2, p) * (3 * x2 * x2) % p
		else:
			l = pow(x1 - x2, p-2, p) * (y1 - y2) % p

		newX = (l ** 2 - x2 - x1) % p
		newY = (l * x2 - l * newX - y2) % p

		return Point(newX, newY)

	def toBytes(self):
		x = self.x.to_bytes(32, "big")
		y = self.y.to_bytes(32, "big")
		return b"\x04" + x + y

def h160(pk): # pvk int
	return ripemd160(sha256((SEC256k1 * pk).toBytes())) # hash160 bytes

def go(pvk):
	h=h160(pvk)
	if h==target_hash:
		print()
		log(f'Found pvk: {hex(pvk)[2:]}\n')
		print('\a', end='', file=sys.stderr)

range_start = 0x80000000000000000
range_end   = 0xfffffffffffffffff
r           = 16384
target_hash = bytes.fromhex('e0b8a2baee1b77fc703455f39d51477451fc8cfc')
th = 24
cnt=1000
seed=0
SEC256k1 = Point()

def main():
	try:
		os.system('cls' if os.name == 'nt' else 'clear')
		print("Puzzle 68 random scanner")
		print("Scanning random addresses in an infinite loop. Press Ctrl+C to stop.\n")

		keys_checked = 0
		start_time = time.time()
		random.seed(seed)

		while True:
			rnd = random.randint(range_start, range_end+1)

			rng = range(rnd, rnd+r)

			with Pool(processes=th) as p:
				for result in p.imap(go, rng):
					keys_checked += 1
					if keys_checked % cnt == 0:
						elapsed = time.time() - start_time
						rate = keys_checked / elapsed
						print(f"\rKeys checked: {keys_checked:,} | Rate: {rate:.2f} keys/sec | Range: {hex(rnd)[2:]}-{hex(rnd+r)[2:]}", end="", flush=True)

	except KeyboardInterrupt:
		print("\n\nScanning stopped by user.")
		print(f"Total keys checked: {keys_checked:,}")

if __name__ == "__main__":
	main()
