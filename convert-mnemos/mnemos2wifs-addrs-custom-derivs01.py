#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations.custom import CustomDerivation
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool, Lock, Manager
from tqdm import tqdm
import os
import sys

OFFSETS = list(range(0, 201)) + [1000, 31337, 65535, 65536] + list(range(1900, 2101))

DERIVATION_TEMPLATES = [
	"m/44'/0'/0'/0/{index}",
	"m/49'/0'/0'/0/{index}",
	"m/84'/0'/0'/0/{index}",
	"m/86'/0'/0'/0/{index}",
]

def process_mnemonic(args):
	mnemonic, lock = args
	lines = []

	for deriv_template in DERIVATION_TEMPLATES:
		for index in OFFSETS:
			try:
				hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_mnemonic(
					mnemonic=BIP39Mnemonic(mnemonic=mnemonic)
				)
				path = deriv_template.format(index=index)
				hdwallet.from_derivation(CustomDerivation(path))

				line = (
					f"{mnemonic}:{path}\n"
					f"{hdwallet.wif(wif_type='wif-compressed')}\n"
					f"{hdwallet.address('P2PKH')}\n"
					f"{hdwallet.address('P2SH')}\n"
					f"{hdwallet.address('P2TR')}\n"
					f"{hdwallet.address('P2WPKH')}\n"
					f"{hdwallet.address('P2WPKH-In-P2SH')}\n"
					f"{hdwallet.address('P2WSH')}\n"
					f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"
				)
				lines.append(line)
			except Exception:
				continue

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
	print(f"Derivation templates: {len(DERIVATION_TEMPLATES)}")
	print(f"Offsets per template: {len(OFFSETS)}")
	print(f"Total paths per mnemonic: {len(DERIVATION_TEMPLATES) * len(OFFSETS)}")
	print('Processing...', flush=True)

	if os.path.exists('output.txt'):
		os.remove('output.txt')

	with Manager() as manager:
		lock = manager.Lock()
		args = [(mnemonic, lock) for mnemonic in mnemonics]

		with Pool(processes=30) as pool:
			list(tqdm(pool.imap_unordered(process_mnemonic, args, chunksize=50), total=len(args)))

	print('\aDone.', file=sys.stderr)

if __name__ == '__main__':
	main()
