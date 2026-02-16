#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys, base58, random

try:
	from hdwallet import HDWallet
	from hdwallet.cryptocurrencies import Bitcoin as BTC
	from hdwallet.hds import BIP32HD
except Exception:
	HDWallet = None

_hdwallet = None

def _init_worker():
	global _hdwallet
	if HDWallet:
		_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	else:
		_hdwallet = None

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(key_hex: str):
	global _hdwallet
	if not _hdwallet:
		return key_hex, ''
	try:
		_hdwallet.from_private_key(private_key=key_hex)
	except Exception:
		return key_hex, ''
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
		f"{_hdwallet.address('P2WSH-In-P2SH')}\n\n"
	)
	return key_hex, out

def gen_keys():
	for i in tqdm(range(0, 1025)):
		random.seed(i)
		for j in range(0, 256):
			k=random.randint(2**j, 2**(j + 1))
			for l in range(k-21, k+21):
				if l<1:
					continue
				yield hex(l)[2:].zfill(64)
		yield None

def main():
	o = open('output.txt', 'w')
	p = open('output2.txt', 'w')

	with Pool(cpu_count(), initializer=_init_worker) as pool:
		for res in pool.imap_unordered(go, (k for k in gen_keys() if k)):
			key, out = res
			o.write(key + '\n')
			p.write(out)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
