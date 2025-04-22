#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
import base58
import hashlib
import os
import sys


start=0x1000000000000000000000000000000000000000000000000000000000000000-int(1e7)
end=0x1000000000000000000000000000000000000000000000000000000000000000+int(1e7)+1


def int_to_bytes4(number, length): # in: int, int
	# length = zero-fill bytes
	return number.to_bytes(length,'big')


def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


o=open('output.txt','w')


def go(x):
	h=hex(x)[2:].zfill(64)
	#print(h)
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=h)
	except Exception as e:
		print(f'Error: {e} @ {h}')
		exit()

	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk)
	w=f'{pvk}\n{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	o.write(w)
	o.flush()


if __name__ == "__main__":
	os.system('cls||clear')
	th=24
	r=range(start, end)
	pbar=tqdm(total=len(r))
	i=0
	cnt=1000
	with Pool(processes=th) as p, tqdm(total=len(r)) as pbar:
		for result in p.imap_unordered(go, r, chunksize=1000):
			i=i+1
			if i%cnt==0:
				pbar.update(cnt)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)
