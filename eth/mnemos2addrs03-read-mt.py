#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from web3 import Web3
import sys

# Alchemy endpoint
ALCHEMY_URL = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
w3.eth.account.enable_unaudited_hdwallet_features()

THREADS = 28
CHUNKSIZE = 1000


def go(m):
	"""Przetwarza pojedynczy mnemonic -> (adres, privkey, mnemonic)"""
	try:
		n = m.decode().strip()
		acc = w3.eth.account.from_mnemonic(n)
		a = w3.to_checksum_address(acc.address)
		p = acc._private_key.hex()
		return f"{a} {p} {n}"
	except Exception:
		return None


def main():
	print("Reading...", flush=True)
	with open("input.txt", "rb") as f:
		infile = f.read().splitlines()

	print("Processing & writing...", flush=True)
	with open("output.txt", "w") as out, Pool(processes=THREADS) as pool, tqdm(total=len(infile)) as pbar:
		for res in pool.imap_unordered(go, infile, chunksize=CHUNKSIZE):
			if res:
				out.write(res + "\n")
				out.flush()  # żeby od razu zapisywało na dysk
			pbar.update()

	# sygnał dźwiękowy po zakończeniu
	print("\a", end="", file=sys.stderr)


if __name__ == "__main__":
	main()
