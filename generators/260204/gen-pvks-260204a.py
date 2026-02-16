#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys, base58, random

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(key_hex: str):
	_hdwallet.from_private_key(private_key=key_hex)
	wif = pvk_to_wif2(key_hex)
	out = (
		f"{key_hex}\n"
		f"{wif}\n"
		f"{_hdwallet.wif()}\n"
		f"{_hdwallet.address('P2PKH')}\n"
		f"{_hdwallet.address('P2SH')}\n"
		f"{_hdwallet.address('P2TR')}\n"
		f"{_hdwallet.address('P2WPKH')}\n"
		f"{_hdwallet.address('P2WPKH-In-P2SH')}\n"
		f"{_hdwallet.address('P2WSH')}\n"
		f"{_hdwallet.address('P2WSH-In-P2SH')}\n"
		f"\n"
	)
	return out

def gen():
	for i in range(0,252,4):
		j=2**i
		for k in range(0,256):
			l=j*k
			for m in range(-100,101):
				n=l+m
				if n<1:
					continue
				yield hex(n)[2:].zfill(64)

def main():
	o = open('output.txt', 'w')

	with Pool(cpu_count()) as pool:
		for res in pool.imap_unordered(go, gen()):
			o.write("".join(res))

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
