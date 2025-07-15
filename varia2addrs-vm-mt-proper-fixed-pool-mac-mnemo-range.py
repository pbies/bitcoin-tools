#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from hdwallet.entropies import BIP39Entropy
from multiprocessing import Pool
from tqdm import tqdm
import base58
import sys

def pvk_to_wif(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def build_wallets(key):
	key = key.strip()
	methods = [
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_mnemonic(BIP39Mnemonic(k)),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(k),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_seed(BIP39Seed(k)),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_wif(k),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_xprivate_key(k),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_entropy(BIP39Entropy(k)),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(base58.b58decode_check(k)[2:].hex()),
		lambda k: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(hex(int(k))[2:])
	]

	wallets = []
	for method in methods:
		try:
			wallets.append(method(key))
		except:
			continue

	for wallet in filter(None, wallets):
		try:
			pvk = int(wallet.private_key(), 16)
		except:
			continue
		for offset in range(-10, 11):
			try:
				pvk_hex = hex(pvk + offset)[2:].zfill(64)
				wif = pvk_to_wif(pvk_hex)
				new_wallet = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(pvk_hex)
				result = (
					f"{key}\n{wif}\n{new_wallet.wif()}\n"
					f"{new_wallet.address('P2PKH')}\n{new_wallet.address('P2SH')}\n"
					f"{new_wallet.address('P2TR')}\n{new_wallet.address('P2WPKH')}\n"
					f"{new_wallet.address('P2WPKH-In-P2SH')}\n{new_wallet.address('P2WSH')}\n"
					f"{new_wallet.address('P2WSH-In-P2SH')}\n\n"
				)
				with open('output.txt', 'a') as outfile:
					outfile.write(result)
			except:
				continue

def main():
	with open('input.txt') as infile:
		lines = [line.strip() for line in infile if line.strip()]

	with Pool(processes=16) as pool, tqdm(total=len(lines)) as pbar:
		for _ in pool.imap_unordered(build_wallets, lines, chunksize=1000):
			pbar.update(1)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
