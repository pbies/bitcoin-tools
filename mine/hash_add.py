#!/usr/bin/env python3

import hashlib
import secp256k1
from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
import dask

with open("btc.bf", "rb") as fp:
	bloom = BloomFilter.load(fp)
addr_countbtc = len(bloom)
print('Total Bitcoin addresses Loaded from Bloomfile: ', str(addr_countbtc))

file1 = open('bitcoin.txt', 'r')

count = 0
# Strips the newline character
@dask.delayed
def search1():
	count = 0
	for line in file1:
		count += 1
		b1 = hashlib.sha256(line.encode()).hexdigest()
		priv = int(b1, base=16)
		add1 = secp256k1.privatekey_to_address(0, True, priv)
		add2 = secp256k1.privatekey_to_address(0, False, priv)
		add3= secp256k1.privatekey_to_address(1, True, priv)
		add4= secp256k1.privatekey_to_address(2, True, priv)
		if add1 in bloom or add2 in bloom or add3 in bloom or add4 in bloom:
			print("MATCH FOUND!!! \nHex ", hex(priv) )
			with open("WINNER.TXT", "a") as f:
				f.write(
					f"""\nWinner!!! \nmath1 {hex(priv)} \nBTC Compressed: {(add1)},\nBTC Unompressed: {(add2)}, \nBTC Segwit: {(add3)},\nBTC Bech31: {(add4)}""""")
		else:
			print("Searching:", hex(priv),line,count, end="\r")

x = dask.delayed(search1())

dask.compute(x)