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
	w = f'{wif1}\n{hdwallet_bip32.wif()}\n{hdwallet_bip32.address("P2PKH")}\n{hdwallet_bip32.address("P2SH")}\n{hdwallet_bip32.address("P2TR")}\n{hdwallet_bip32.address("P2WPKH")}\n{hdwallet_bip32.address("P2WPKH-In-P2SH")}\n{hdwallet_bip32.address("P2WSH")}\n{hdwallet_bip32.address("P2WSH-In-P2SH")}\n\n'
	with open(outfile_path, 'a') as outfile:
		outfile.write(w)

for i in range(0, 64):
	for j in range(1, 0x10):
		x=hex(j)[2:]+i*'0'
		y=x.zfill(64)
		job(y)

def process_batch(line):
	k = line.strip()

if __name__ == "__main__":
	size = os.path.getsize(infile_path)
	c=0
	with open(infile_path, 'rb') as infile, Pool(processes=num_processes) as pool, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for results in pool.imap_unordered(process_batch, infile, chunksize=1000):
			tmp=infile.tell()
			pbar.update(tmp-c)
			c=tmp

	print('\a', end='', file=sys.stderr)
