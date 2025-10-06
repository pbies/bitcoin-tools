#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, os

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	k=k.rstrip(b'\n').decode().zfill(64)
	try:
		hdwallet_bip32 = hdwallet.from_private_key(private_key=k)
	except:
		return
	wif=pvk_to_wif2(k)
	a = f'{k}\n{wif}\n{hdwallet_bip32.wif()}\n{hdwallet_bip32.address("P2PKH")}\n{hdwallet_bip32.address("P2SH")}\n{hdwallet_bip32.address("P2TR")}\n{hdwallet_bip32.address("P2WPKH")}\n{hdwallet_bip32.address("P2WPKH-In-P2SH")}\n{hdwallet_bip32.address("P2WSH")}\n{hdwallet_bip32.address("P2WSH-In-P2SH")}\n\n'
	with open('output.txt', 'a') as outfile:
		outfile.write(a)

def main():
	size = os.path.getsize('input.txt')
	tmp = 0
	cnt = 100000
	th=24
	i=0
	infile = open('input.txt','rb')
	outfile = open('output.txt','w')
	with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			pos=infile.tell()
			r=pos-tmp
			if r>cnt:
				tmp=pos
				pbar.update(r)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
