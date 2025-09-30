#!/usr/bin/env python3

# bad!

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm.contrib.concurrent import process_map
import base58
import os

INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
THREADS = 24

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_key(k):
	k = k.decode().strip()
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=k)
	except Exception:
		return None
	
	wif = pvk_to_wif2(k)
	addresses = "\n".join([
		wif,
		hdwallet.wif(),
		hdwallet.address("P2PKH"),
		hdwallet.address("P2SH"),
		hdwallet.address("P2TR"),
		hdwallet.address("P2WPKH"),
		hdwallet.address("P2WPKH-In-P2SH"),
		hdwallet.address("P2WSH"),
		hdwallet.address("P2WSH-In-P2SH"),
		""
	])
	outfile.writelines(filter(None, addresses))
	outfile.flush()

def main():
	file_size = os.path.getsize(INPUT_FILE)
	
	with open(INPUT_FILE, "rb") as infile, open(OUTPUT_FILE, "w") as outfile:
		keys = infile
		process_map(process_key, keys, max_workers=THREADS, chunksize=1000)

if __name__ == "__main__":
	main()
