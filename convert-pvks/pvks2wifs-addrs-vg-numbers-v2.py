#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import sys, base58, os

outfile_path = 'output.txt'
num_processes = 24
hdwallet_bip32 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def job(x):
	try:
		hdwallet_bip32.from_private_key(private_key=x)
	except:
		return
	wif1 = pvk_to_wif2(x)
	w = f'{x}\n{wif1}\n{hdwallet_bip32.wif()}\n{hdwallet_bip32.address("P2PKH")}\n{hdwallet_bip32.address("P2SH")}\n{hdwallet_bip32.address("P2TR")}\n{hdwallet_bip32.address("P2WPKH")}\n{hdwallet_bip32.address("P2WPKH-In-P2SH")}\n{hdwallet_bip32.address("P2WSH")}\n{hdwallet_bip32.address("P2WSH-In-P2SH")}\n\n'
	with open(outfile_path, 'a') as outfile:
		outfile.write(w)

def gen():
	for i in tqdm(range(1, 4097)):
		for j in range(1, 256):
			for k in range(-1024, 1025):
				n=hex((i<<j)+k)[2:].zfill(64)
				yield n

if __name__ == "__main__":
	open(outfile_path, 'w').close()
	with Pool(processes=num_processes) as pool:
		for results in pool.imap_unordered(job, gen(), chunksize=10000):
			pass

	print('\a', end='', file=sys.stderr)
