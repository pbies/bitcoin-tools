#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import cpu_count
from tqdm.contrib.concurrent import process_map
import base58

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_input(k):
	results = []
	for j in range(1900, 2021):
		h = hex(k + j)[2:].zfill(64)
		try:
			hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=h)
		except Exception:
			continue
		wif = pvk_to_wif2(h)
		entry = (
			f'{h}\n{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n'
			f'{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n'
			f'{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n'
			f'{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
		)
		results.append(entry)
	return results

def generate_inputs():
	for i in range(2, 1025):
		for j in range(2, 1025):
			yield (i ** j) % (2 ** 256)

if __name__ == '__main__':
	import os, sys
	os.system('cls||clear')

	inputs = list(generate_inputs())
	num_workers = min(15, cpu_count())

	# Use tqdm's process_map to show progress
	all_results = process_map(process_input, inputs, max_workers=num_workers, chunksize=1)

	with open('output.txt', 'w') as f:
		for result_list in all_results:
			for entry in result_list:
				f.write(entry)

	print('\a', end='', file=sys.stderr)
