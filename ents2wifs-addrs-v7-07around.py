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
import datetime

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open('log.txt', 'a') as log_file:
		log_file.write(f'{timestamp} {message}\n')
	print(f'{timestamp} {message}', flush=True)

def go(args):
	ent_hex, lock = args
	result_lines = []

	i=int(ent_hex,16)

	for j in range(-5,6):
		k=hex(i+j)[2:].zfill(32)
		try:
			hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_entropy(entropy=BIP39Entropy(k))
		except Exception as e:
			log(f'Error with {k} - {e}')
			continue

		wif = pvk_to_wif2(hdwallet.private_key())

		line = f"{k}\n{wif}\n{hdwallet.wif()}\n"
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
	th=28

	os.system('cls' if os.name == 'nt' else 'clear')
	print('Loading entropies...', flush=True)

	if not os.path.exists('input.txt'):
		print('Missing input.txt file!', file=sys.stderr)
		sys.exit(1)

	with open('input.txt') as f:
		raw = [line.strip() for line in f if line.strip()]

	print(f"Total entropies loaded: {len(raw)}")
	print('Processing...', flush=True)

	if os.path.exists("output.txt"):
		os.remove("output.txt")

	with Manager() as manager:
		lock = manager.Lock()
		args_list = [(ent, lock) for ent in raw]

		with Pool(processes=th) as pool:
			list(tqdm(pool.imap_unordered(go, args_list, chunksize=th*4), total=len(args_list)))

	print('\aDone.', file=sys.stderr)
