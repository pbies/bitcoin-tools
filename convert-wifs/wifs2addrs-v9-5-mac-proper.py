#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

#from hdwallet.symbols import BTC
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

outfile = open('output.txt','w')

def go(k):
	try:
		hdwallet.from_wif(wif=k)
		pvk=hdwallet.private_key()
		wif=pvk_to_wif2(pvk).decode()
	except:
		return
	r=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(r)
	outfile.flush()

def main():
	print('Reading...', flush=True)
	infile = open('input.txt','r')
	lines = infile.read().splitlines()

	print('Writing...', flush=True)
	process_map(go, lines, max_workers=8, chunksize=1000)

	print('\a',end='',file=sys.stderr)

if __name__ == '__main__':
	main()
