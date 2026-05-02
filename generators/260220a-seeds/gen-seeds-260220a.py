#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys, base58, random

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.seeds import BIP39Seed

_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(key_hex):
	#print(key_hex)
	_hdwallet.from_seed(seed=BIP39Seed(key_hex))
	pvk=_hdwallet.private_key()
	wif = pvk_to_wif2(pvk)
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
	for i in range(0, 512):
		j=2**i
		for k in range(-100, 101):
			r=j+k
			if r<1:
				continue
			yield hex(r)[2:].zfill(128)

def main():
	o = open('output.txt', 'w')

	t=tqdm(total=512*200)
	with Pool(cpu_count()) as pool:
		for res in pool.imap_unordered(go, gen()):
			o.write("".join(res))
			t.update()

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
