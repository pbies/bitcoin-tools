#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD, BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import sys, base58, os

infile_path = 'input.txt'
outfile_path = 'output.txt'
num_processes = 28
minus=8
plus=101

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_batch(line):
	hdwallet_bip32 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdwallet_bip84 = HDWallet(cryptocurrency=BTC, hd=BIP84HD)
	k = line.strip()
	try:
		i = int(k, 16)
		for j in range(i - minus, i + plus):
			l = hex(j)[2:].zfill(64)
			try:
				hdwallet_bip32.from_private_key(private_key=l)
				hdwallet_bip84.from_private_key(private_key=l)
			except:
				continue
			pvk1 = hdwallet_bip32.private_key()
			pvk2 = hdwallet_bip84.private_key()
			wif1 = pvk_to_wif2(pvk1)
			wif2 = pvk_to_wif2(pvk2)
			w = f'{wif1}\n{hdwallet_bip32.wif()}\n{hdwallet_bip32.address("P2PKH")}\n{hdwallet_bip32.address("P2SH")}\n{hdwallet_bip32.address("P2TR")}\n{hdwallet_bip32.address("P2WPKH")}\n{hdwallet_bip32.address("P2WPKH-In-P2SH")}\n{hdwallet_bip32.address("P2WSH")}\n{hdwallet_bip32.address("P2WSH-In-P2SH")}\n\n'
			w += f'{wif2}\n{hdwallet_bip84.wif()}\n{hdwallet_bip84.address("P2PKH")}\n{hdwallet_bip84.address("P2SH")}\n{hdwallet_bip84.address("P2TR")}\n{hdwallet_bip84.address("P2WPKH")}\n{hdwallet_bip84.address("P2WPKH-In-P2SH")}\n{hdwallet_bip84.address("P2WSH")}\n{hdwallet_bip84.address("P2WSH-In-P2SH")}\n\n'
			outfile.write(w)
			outfile.flush()
	except ValueError:
		pass

if __name__ == "__main__":
	size = os.path.getsize(infile_path)
	c=0
	with open(infile_path, 'rb') as infile, open(outfile_path, 'w') as outfile, Pool(processes=num_processes) as pool, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for results in pool.imap_unordered(process_batch, infile, chunksize=1000):
			tmp=infile.tell()
			pbar.update(tmp-c)
			c=tmp

	print('\a', end='', file=sys.stderr)
