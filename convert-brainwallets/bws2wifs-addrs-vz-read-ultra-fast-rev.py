#!/usr/bin/env python3

from multiprocessing import Pool, Process, Queue, cpu_count
from tqdm import tqdm
import os, sys
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

CHUNK_LINES     = 200
IPC_CHUNKSIZE   = 1
ADDR_TYPES      = ('P2PKH', 'P2SH', 'P2TR', 'P2WPKH', 'P2WPKH-In-P2SH', 'P2WSH', 'P2WSH-In-P2SH')
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

_hw = None

def init_worker():
	global _hw
	_hw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def process_block(lines):
	global _hw
	hw = _hw
	parts = []
	byte_count = 0

	for line in lines:
		byte_count += len(line)
		raw = line.rstrip(b'\n')
		label = raw.decode('utf-8', errors='replace')

		try:
			i = int(raw, 16)
		except ValueError:
			continue

		for x in range(-3, 4):
			j = i + x
			for y in range(1, 33):
				k = j * y % 0x10000000000000000000000000000000000000000000000000000000000000000
				for z in range(-3, 4):
					l = k + z
					if l <= 0 or l >= SECP256K1_ORDER:
						continue
					m = format(l, '064x')
					try:
						hw.from_private_key(private_key=m)
					except Exception:
						sys.stderr.write(f"bad key: {m}\n")
						continue
					wif   = hw.wif(wif_type='wif')
					wif_c = hw.wif(wif_type='wif-compressed')
					addrs = '\n'.join(hw.address(a) for a in ADDR_TYPES)
					parts.append(f"{label}\n{wif}\n{wif_c}\n{addrs}\n\n")

	return ''.join(parts), byte_count

def writer_process(out_path, queue):
	with open(out_path, 'a', buffering=4 * 1024 * 1024) as fo:
		while True:
			item = queue.get()
			if item is None:
				fo.flush()
				break
			fo.write(item)
			fo.flush()

def read_blocks(path, chunk_size=CHUNK_LINES):
	with open(path, 'rb', buffering=16 * 1024 * 1024) as f:
		block = []
		for line in f:
			block.append(line)
			if len(block) >= chunk_size:
				yield block
				block = []
		if block:
			yield block

def main():
	inp = 'input.txt'
	out = 'output.txt'

	if not os.path.exists(inp):
		sys.stderr.write(f"Error: {inp} not found!\n")
		return

	open(out, 'w').close()
	workers = max(1, cpu_count() - 2)
	sys.stderr.write(f"Using {workers} worker processes\n")

	q = Queue(maxsize=workers * 4)
	writer = Process(target=writer_process, args=(out, q), daemon=True)
	writer.start()

	with Pool(workers, initializer=init_worker) as p, \
		 tqdm(total=os.path.getsize(inp), unit='B', unit_scale=True, desc="Processing") as bar:

		try:
			for result_str, byte_count in p.imap_unordered(
				process_block, read_blocks(inp), chunksize=IPC_CHUNKSIZE
			):
				if result_str:
					q.put(result_str)
				bar.update(byte_count)
		finally:
			q.put(None)
			writer.join()

	sys.stderr.write('\nDone!\n\a')

if __name__ == '__main__':
	main()
