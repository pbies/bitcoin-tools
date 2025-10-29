#!/usr/bin/env python3

import os, sys, hashlib, base58
from multiprocessing import get_context
from tqdm import tqdm
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

def pvk_to_wif2(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes).decode()

def init_worker():
	global hdwallet
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def go(x):
	x = x.rstrip(b'\n')
	sha = hashlib.sha256(x).digest()
	try:
		hdwallet.from_private_key(private_key=sha.hex())
	except Exception:
		return None
	out = (
		f"{x.decode()}\n"
		f"{pvk_to_wif2(sha)}\n"
		f"{hdwallet.wif()}\n"
		f"{hdwallet.address('P2PKH')}\n"
		f"{hdwallet.address('P2SH')}\n"
		f"{hdwallet.address('P2TR')}\n"
		f"{hdwallet.address('P2WPKH')}\n"
		f"{hdwallet.address('P2WPKH-In-P2SH')}\n"
		f"{hdwallet.address('P2WSH')}\n"
		f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"
	)
	return out

def main():
	th = 24
	cnt = 100000
	with open('input.txt', 'rb') as infile:
		size = os.path.getsize('input.txt')
		open('output.txt','w').close()
		with get_context("fork").Pool(processes=th, initializer=init_worker) as p, \
			tqdm(total=size, unit='B', unit_scale=True) as pbar:

			tmp = 0
			for result in p.imap_unordered(go, infile, chunksize=5000):
				if result:
					with open('output.txt','a') as outfile:
						outfile.write(result)
				pos = infile.tell()
				diff = pos - tmp
				if diff > cnt:
					tmp = pos
					pbar.update(diff)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
