#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.seeds import BIP39Seed
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys, base58, os

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def gen():
	x=0
	while True:
		x+=1
		yield hex((6*x)-1)[2:].zfill(64), hex((6*x)+1)[2:].zfill(64)

def worker(args):
	x, y=args

	_hdwallet.from_private_key(x)
	pvk=_hdwallet.private_key()
	wif = pvk_to_wif2(x)

	out = (
		f"{x}\n"
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

	_hdwallet.from_private_key(y)
	pvk=_hdwallet.private_key()
	wif = pvk_to_wif2(y)

	out2 = (
		f"{y}\n"
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

	with open('output.txt','a') as o:
		o.write(out)
		o.write(out2)
		o.flush()

def main():
	open('output.txt','w').close()

	with Pool(cpu_count()) as pool:
		for result in tqdm(pool.imap_unordered(worker, gen(), chunksize=100)):
			if os.path.getsize('output.txt')>=10**10:
				sys.exit(0)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
