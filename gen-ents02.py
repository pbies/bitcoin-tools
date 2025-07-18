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
import json

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

OFFSETS = [0, 1, 64, 100, 1000, 31337, 65535, 65536]
OFFSETS.extend(list(range(1940,2026)))

def go(args):
	ent_hex, lock = args
	result_lines = []

	# try:
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_entropy(entropy=BIP39Entropy(ent_hex))

	for index in OFFSETS:  # 0..100 derivations
		# try:
		custom_derivation = CustomDerivation(f"m/84'/0'/0'/0/{index}")
		child_wallet = hdwallet.from_derivation(custom_derivation)

		wif = pvk_to_wif2(child_wallet.private_key())

		line = f"{ent_hex}:{index}\n{wif}\n{child_wallet.wif()}\n"
		line += f"{child_wallet.address('P2PKH')}\n{child_wallet.address('P2SH')}\n"
		line += f"{child_wallet.address('P2TR')}\n{child_wallet.address('P2WPKH')}\n"
		line += f"{child_wallet.address('P2WPKH-In-P2SH')}\n{child_wallet.address('P2WSH')}\n"
		line += f"{child_wallet.address('P2WSH-In-P2SH')}\n\n"

		result_lines.append(line)

			# except Exception:
				# continue

	# except Exception:
		# return None

	if result_lines:
		with lock:
			with open("output.txt", "a") as outfile:
				outfile.writelines(result_lines)

if __name__ == '__main__':
	os.system('cls||clear')

	if os.path.exists("output.txt"):
		os.remove("output.txt")

	i_range = list(range(2, 128))
	j_range = list(range(2, 16384))

	candidates = set()

	if os.path.exists("cand.txt"):
		print('Loading...')
		with open("cand.txt","r") as fh:
			candidates=json.load(fh)
		print(f'Loaded {len(candidates)} unique candidates.')
	else:
		for i in tqdm(i_range, desc='Generating candidates'):
			for j in j_range:
				base = pow(i, j, 1 << 128)
				for z in OFFSETS:
					candidate = base + z
					if 1 <= candidate < (1 << 128):
						candidates.add(candidate)
		print(f'Generated {len(candidates)} unique candidates.')
		with open("cand.txt","w") as fh:
			json.dump(list(candidates), fh)

	with Manager() as manager:
		lock = manager.Lock()
		print('Converting...')
		args_list = [(hex(ent)[2:].zfill(32), lock) for ent in candidates]

		print('Main loop...')
		with Pool(processes=15) as pool:
			list(tqdm(pool.imap_unordered(go, args_list, chunksize=50), total=len(args_list)))

	print('\aDone.', file=sys.stderr)
