#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import sys, base58, os
from tqdm.contrib.concurrent import process_map

outfile_path = 'output.txt'

max=1<<256

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def gen():
	for i in tqdm(range(1, 255)):
		for j in range(1, 257):
			for k in range(-1024, 1025):
				n=hex(abs(((i<<j)+k)%max))[2:].zfill(64)
				yield n

def go(x):
	try:
		hdwallet.from_private_key(private_key=x)
	except:
		return
	wif = pvk_to_wif2(x)
	a = (
		f"{x}\n"
		f"{wif}\n"
		f"{hdwallet.wif()}\n"
		f"{hdwallet.address('P2PKH')}\n"
		f"{hdwallet.address('P2SH')}\n"
		f"{hdwallet.address('P2TR')}\n"
		f"{hdwallet.address('P2WPKH')}\n"
		f"{hdwallet.address('P2WPKH-In-P2SH')}\n"
		f"{hdwallet.address('P2WSH')}\n"
		f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"
	)

	with open(outfile_path, 'a') as outfile:
		outfile.write(f'{a}\n')

def main():
	keys=set(gen())
	print(f"Generated {len(keys)} unique keys")
	with Pool(processes=24) as p, tqdm(total=len(keys)) as pbar:
		for _ in p.imap_unordered(go, keys, chunksize=100):
			pbar.update(1)
	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
