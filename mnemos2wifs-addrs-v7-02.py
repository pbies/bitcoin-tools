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

def pvk_to_wif(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

OFFSETS = [0, 1, 64, 100, 1000, 31337, 65535, 65536] + list(range(1940, 2026))

def process_mnemonic(args):
	mnemonic, lock = args
	lines = []

	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=mnemonic))

		for index in OFFSETS:
			try:
				child_wallet = hdwallet.from_derivation(CustomDerivation(f"m/84'/0'/0'/0/{index}"))
				wif_manual = pvk_to_wif(child_wallet.private_key())

				line = (
					f"{mnemonic}:{index}\n{wif_manual}\n{child_wallet.wif()}\n"
					f"{child_wallet.address('P2PKH')}\n{child_wallet.address('P2SH')}\n"
					f"{child_wallet.address('P2TR')}\n{child_wallet.address('P2WPKH')}\n"
					f"{child_wallet.address('P2WPKH-In-P2SH')}\n{child_wallet.address('P2WSH')}\n"
					f"{child_wallet.address('P2WSH-In-P2SH')}\n\n"
				)
				lines.append(line)
			except Exception:
				continue

	except Exception:
		return

	if lines:
		with lock:
			with open("output.txt", "a") as f:
				f.writelines(lines)

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Loading mnemonics...', flush=True)

	if not os.path.exists('input.txt'):
		print('Error: Missing input.txt!', file=sys.stderr)
		sys.exit(1)

	with open('input.txt') as f:
		mnemonics = [line.strip() for line in f if line.strip()]

	print(f"Total mnemonics loaded: {len(mnemonics)}")
	print('Processing...', flush=True)

	if os.path.exists('output.txt'):
		os.remove('output.txt')

	with Manager() as manager:
		lock = manager.Lock()
		args = [(mnemonic, lock) for mnemonic in mnemonics]

		with Pool(processes=15) as pool:
			list(tqdm(pool.imap_unordered(process_mnemonic, args, chunksize=50), total=len(args)))

	print('\aDone.', file=sys.stderr)

if __name__ == '__main__':
	main()
