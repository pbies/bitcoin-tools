#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations.custom import CustomDerivation
from hdwallet.hds import BIP32HD
from hdwallet.seeds import BIP39Seed
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

	if len(ent_hex) != 128:
		return None  # Expecting 128 hex digits (64 bytes)

	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_seed(seed=BIP39Seed(ent_hex))

		for a in [0, 1, 2]:
			for b in [0, 1, 2]:
				for c in [0, 1, 2]:
					for index in range(0, 6):
						try:
							custom_derivation = CustomDerivation(f"m/84'/{a}'/{b}'/{c}/{index}")
							child_wallet = hdwallet.from_derivation(custom_derivation)

							wif = pvk_to_wif2(child_wallet.private_key())

							line = f"{ent_hex}:{a}/{b}/{c}/{index}\n{wif}\n{child_wallet.wif()}\n"
							line += f"{child_wallet.address('P2PKH')}\n{child_wallet.address('P2SH')}\n"
							line += f"{child_wallet.address('P2TR')}\n{child_wallet.address('P2WPKH')}\n"
							line += f"{child_wallet.address('P2WPKH-In-P2SH')}\n{child_wallet.address('P2WSH')}\n"
							line += f"{child_wallet.address('P2WSH-In-P2SH')}\n\n"

							result_lines.append(line)

						except Exception as e:
							log(f'Error with {ent_hex}:{a}/{b}/{c}/{index} - {e}')
							continue

		if result_lines:
			with lock:
				with open("output.txt", "a") as outfile:
					outfile.writelines(result_lines)

	except Exception as e:
		print(f'Error occured: {e}')
		pass

if __name__ == '__main__':
	th=15

	os.system('cls||clear')
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
