#!/usr/bin/env python3

from bip_utils import Bip44, Bip84, Bip84Coins, Bip39EntropyGenerator, Bip39SeedGenerator, Bip32Utils, Bip39MnemonicGenerator, Bip44Changes, Bip49, Bip49Coins, Bip44Coins
from multiprocessing import Pool, Lock, Manager
from threading import Lock
from tqdm import tqdm
import base58
import hashlib
import os
import sys

def pvk_to_wif2(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes).decode()

OFFSETS = [-65536, -65535, -31337, -1000, -100, -64, 0, 1, 64, 100, 1000, 31337, 65535, 65536]

def worker_task(x):
	results = []
	y = hex(x)[2:].zfill(32)
	entropy_bytes = bytes.fromhex(y)
	mnemonic = Bip39MnemonicGenerator().FromEntropy(entropy_bytes)
	seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

	#try:
	bip84_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
	bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
	bip49_ctx = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
	for p in range(0, 101):
		addr84 = bip84_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(p)
		addr44 = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(p)
		addr49 = bip49_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(p)

		p1=addr84.PrivateKey().Raw().ToHex()
		p1b=addr84.PrivateKey().Raw().ToBytes()
		p2=addr44.PrivateKey().Raw().ToHex()
		p2b=addr44.PrivateKey().Raw().ToBytes()
		p3=addr49.PrivateKey().Raw().ToHex()
		p3b=addr49.PrivateKey().Raw().ToBytes()

		results.append(
			f"{y}:{p}\n"
			f"{p1}\n"
			f"{p2}\n"
			f"{p3}\n"
			f"{addr84.PrivateKey().ToWif()}\n"
			f"{private_key_to_uncompressed_wif(p1b)}\n"
			f"{addr44.PrivateKey().ToWif()}\n"
			f"{private_key_to_uncompressed_wif(p2b)}\n"
			f"{addr49.PrivateKey().ToWif()}\n"
			f"{private_key_to_uncompressed_wif(p3b)}\n"
			f"{addr84.PublicKey().ToAddress()}\n"
			f"{addr44.PublicKey().ToAddress()}\n"
			f"{addr49.PublicKey().ToAddress()}\n\n"
		)
	#except Exception:
	#	pass

	return results

file_lock = Lock()

def save_results(results, output_file):
	with file_lock:
		with open(output_file, 'a') as f:
			for r in results:
				f.write(r)

def private_key_to_uncompressed_wif(priv_key_bytes):
	extended_key = b'\x80' + priv_key_bytes  # 0x80 + raw priv key
	checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
	return base58.b58encode(extended_key + checksum).decode()

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Getting ready...', flush=True)

	i_range = list(range(2, 129))
	j_range = list(range(2, 65536))

	candidates = set()
	for i in tqdm(i_range, desc='Generating candidates'):
		for j in j_range:
			base = pow(i, j, 1 << 128)
			for z in OFFSETS:
				candidate = base + z
				if 1 <= candidate < (1 << 128):
					candidates.add(candidate)

	print(f'Generated {len(candidates)} unique candidates.')
	output_file = 'output.txt'
	open(output_file, 'w').close()

	with Manager() as manager:
		with Pool(processes=15) as pool:
			for results in tqdm(pool.imap_unordered(worker_task, candidates, chunksize=100), total=len(candidates), desc='Processing'):
				save_results(results, output_file)

	print('\aDone.', file=sys.stderr)

if __name__ == '__main__':
	main()
