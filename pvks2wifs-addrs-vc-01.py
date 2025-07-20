#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations.custom import CustomDerivation
from hdwallet.hds import BIP32HD
from hdwallet.entropies import BIP39Entropy
from multiprocessing import Pool, Lock, Manager
from tqdm import tqdm
import base58
import os
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(args):
	pvk_hex, lock = args
	result_lines = []

	if len(pvk_hex) != 64:
		return None  # Expecting 128 hex digits (64 bytes)

	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(pvk_hex)

	wif = pvk_to_wif2(hdwallet.private_key())

	line = f"{pvk_hex}\n{wif}\n{hdwallet.wif()}\n"
	line += f"{hdwallet.address('P2PKH')}\n{hdwallet.address('P2SH')}\n"
	line += f"{hdwallet.address('P2TR')}\n{hdwallet.address('P2WPKH')}\n"
	line += f"{hdwallet.address('P2WPKH-In-P2SH')}\n{hdwallet.address('P2WSH')}\n"
	line += f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"

	result_lines.append(line)

	if result_lines:
		with lock:
			with open("output.txt", "a") as outfile:
				outfile.writelines(result_lines)

if __name__ == '__main__':
	os.system('cls||clear')
	print('Loading pvks...', flush=True)

	if not os.path.exists('input.txt'):
		print('Missing input.txt file!', file=sys.stderr)
		sys.exit(1)

	with open('input.txt') as f:
		raw = [line.strip() for line in f if line.strip()]

	print(f"Total pvks loaded: {len(raw)}")
	print('Processing...', flush=True)

	if os.path.exists("output.txt"):
		os.remove("output.txt")

	with Manager() as manager:
		lock = manager.Lock()
		args_list = [(pvk, lock) for pvk in raw]

		with Pool(processes=15) as pool:
			list(tqdm(pool.imap_unordered(go, args_list, chunksize=50), total=len(args_list)))

	print('\aDone.', file=sys.stderr)
