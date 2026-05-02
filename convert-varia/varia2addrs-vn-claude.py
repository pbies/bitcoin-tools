#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from hdwallet.entropies import BIP39Entropy
from multiprocessing import Pool, Manager
from tqdm import tqdm
import base58
import sys
import os

OUTPUT_FILE = 'output.txt'

def pvk_to_wif(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def get_addresses(wallet):
	return (
		wallet.address('P2PKH'),
		wallet.address('P2SH'),
		wallet.address('P2TR'),
		wallet.address('P2WPKH'),
		wallet.address('P2WPKH-In-P2SH'),
		wallet.address('P2WSH'),
		wallet.address('P2WSH-In-P2SH'),
	)

def build_wallets(key):
	key = key.strip()
	if not key:
		return

	methods = [
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_mnemonic(BIP39Mnemonic(k)),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(k),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_seed(BIP39Seed(k)),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_wif(k),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_xprivate_key(k),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_entropy(BIP39Entropy(k)),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(base58.b58decode_check(k)[2:].hex()),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(hex(int(k))[2:]),
	]

	results = []

	for method in methods:
		try:
			wallet = method(key)
			if wallet is None:
				continue
			pvk_hex = wallet.private_key()
			if not pvk_hex:
				continue
			wif = pvk_to_wif(pvk_hex)
			p2pkh, p2sh, p2tr, p2wpkh, p2wpkh_p2sh, p2wsh, p2wsh_p2sh = get_addresses(wallet)
			result = (
				f"{key}\n{wif}\n{wallet.wif()}\n"
				f"{p2pkh}\n{p2sh}\n{p2tr}\n{p2wpkh}\n"
				f"{p2wpkh_p2sh}\n{p2wsh}\n{p2wsh_p2sh}\n\n"
			)
			results.append(result)
		except Exception:
			continue

	if results:
		with open(OUTPUT_FILE, 'a') as outfile:
			outfile.writelines(results)

def main():
	if not os.path.exists('input.txt'):
		print("Error: input.txt not found.", file=sys.stderr)
		sys.exit(1)

	with open('input.txt') as infile:
		lines = [line.strip() for line in infile if line.strip()]

	if not lines:
		print("No input lines to process.", file=sys.stderr)
		sys.exit(0)

	# Clear or create output file
	open(OUTPUT_FILE, 'w').close()

	num_workers = min(16, os.cpu_count() or 4)

	with Pool(processes=num_workers) as pool, tqdm(total=len(lines), desc="Processing") as pbar:
		for _ in pool.imap_unordered(build_wallets, lines, chunksize=100):
			pbar.update(1)

	print('\a', end='', file=sys.stderr)
	print(f"Done. Results saved to {OUTPUT_FILE}")

if __name__ == '__main__':
	main()
