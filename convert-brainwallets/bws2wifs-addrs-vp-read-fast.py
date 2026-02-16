#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from bitcash import Key
from tqdm import tqdm
import os, hashlib, base58, sys
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

CHUNK_LINES = 10

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_block(lines):
	out = []
	for line in lines:
		line = line.rstrip(b'\n')
		sha = hashlib.sha256(line).digest()
		h=sha.hex()
		hdwallet.from_private_key(private_key=h)
		wif = pvk_to_wif2(h)
		a = (
			f"{line}\n"
			f"{wif}\n"
			f"{hdwallet.wif()}\n"
			f"{hdwallet.address('P2PKH')}\n"
			f"{hdwallet.address('P2SH')}\n"
			f"{hdwallet.address('P2TR')}\n"
			f"{hdwallet.address('P2WPKH')}\n"
			f"{hdwallet.address('P2WPKH-In-P2SH')}\n"
			f"{hdwallet.address('P2WSH')}\n"
			f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"
		)

		out.append(
			a
		)
	return ''.join(out)

def read_blocks(path):
	with open(path, 'rb', buffering=1024*1024) as f:
		block = []
		for line in f:
			block.append(line)
			if len(block) >= CHUNK_LINES:
				yield block
				block = []
		if block:
			yield block

def main():
	inp = 'input.txt'
	out = 'output.txt'

	total_bytes = os.path.getsize(inp)

	with open(out, 'w'):
		pass

	workers = cpu_count()

	with Pool(workers) as p, open(out, 'a', buffering=1024*1024) as fo, \
		tqdm(total=total_bytes, unit='B', unit_scale=True) as bar:

		for block, result in zip(
			read_blocks(inp),
			p.imap_unordered(process_block, read_blocks(inp), chunksize=5)
		):
			fo.write(result)
			bar.update(sum(len(line) for line in block))

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
