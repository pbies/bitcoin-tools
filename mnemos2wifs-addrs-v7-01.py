#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations.custom import CustomDerivation
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool, Lock, Manager
from tqdm import tqdm
import base58
import os
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

OFFSETS = [0, 1, 64, 100, 1000, 31337, 65535, 65536]
OFFSETS.extend(list(range(1940,2026)))

def go(args):
	mnemo, lock = args
	result_lines = []

	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=mnemo))

		for index in OFFSETS:
			try:
				custom_derivation = CustomDerivation(f"m/84'/0'/0'/0/{index}")
				child_wallet = hdwallet.from_derivation(custom_derivation)

				wif = pvk_to_wif2(child_wallet.private_key())

				line = f"{mnemo}:{index}\n{wif}\n{child_wallet.wif()}\n"
				line += f"{child_wallet.address('P2PKH')}\n{child_wallet.address('P2SH')}\n"
				line += f"{child_wallet.address('P2TR')}\n{child_wallet.address('P2WPKH')}\n"
				line += f"{child_wallet.address('P2WPKH-In-P2SH')}\n{child_wallet.address('P2WSH')}\n"
				line += f"{child_wallet.address('P2WSH-In-P2SH')}\n\n"

				result_lines.append(line)

			except Exception:
				continue

	except Exception:
		return None

	if result_lines:
		with lock:
			with open("output.txt", "a") as outfile:
				outfile.writelines(result_lines)

if __name__ == '__main__':
	os.system('cls||clear')
	print('Loading mnemos...', flush=True)

	if not os.path.exists('input.txt'):
		print('Missing input.txt file!', file=sys.stderr)
		sys.exit(1)

	with open('input.txt') as f:
		raw = [line.strip() for line in f if line.strip()]

	print(f"Total mnemos loaded: {len(raw)}")
	print('Processing...', flush=True)

	if os.path.exists("output.txt"):
		os.remove("output.txt")

	with Manager() as manager:
		lock = manager.Lock()
		args_list = [(m, lock) for m in raw]

		with Pool(processes=15) as pool:
			list(tqdm(pool.imap_unordered(go, args_list, chunksize=50), total=len(args_list)))

	print('\aDone.', file=sys.stderr)
