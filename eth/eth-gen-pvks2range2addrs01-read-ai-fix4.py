#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from tqdm import tqdm
from web3 import Web3
import multiprocessing as mp
import sys, base58, os
import threading
import time

# very fast

# Funkcja konwertująca hex na WIF
def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

# Robota dla jednej pary (i, j)
def compute_pair_task(pair):
	i, j = pair
	base = (1 << i) % (1<<256)
	result = []
	cv = Curve.get_curve('secp256k1')
	for z in OFFSETS:
		private_key = base * j + z
		if private_key < 1:
			continue
		try:
			pu_key = private_key * cv.generator
			concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
		except:
			continue
		k = keccak.new(digest_bits=256)
		k.update(concat_x_y)
		eth_addr = '0x' + k.hexdigest()[-40:]
		cksum = Web3.to_checksum_address(eth_addr)
		p = hex(private_key)[2:].zfill(64)
		a = f'{cksum} {p}\n'
		result.append(a)
	return result

# Wątek zapisujący dane z kolejki do pliku
def writer_thread(q, stop_event):
	with open('output.txt', 'w', buffering=1) as f:
		while not stop_event.is_set() or not q.empty():
			try:
				data = q.get(timeout=0.1)
				f.write(data)
			except:
				continue

# Parametry i stałe
OFFSETS = [-65536, -65535, -31337, -1024, -1000, -100, -64, -2, -1, 0, 1, 2, 64, 100, 1000, 1024, 31337, 65535, 65536]
PROCESSES = 6

# Czyszczenie terminala
os.system('cls' if os.name == 'nt' else 'clear')

# Zakresy do przetworzenia
i_range = list(range(2, 256))
j_range = list(range(2, 256))
pairs = [(i, j) for i in i_range for j in j_range]
total = len(pairs)

# Kolejka i synchronizacja
manager = mp.Manager()
q = manager.Queue()
stop_event = mp.Event()

# Pasek postępu
pbar = tqdm(total=total)

# Start wątku zapisującego
writer = threading.Thread(target=writer_thread, args=(q, stop_event))
writer.start()

# Funkcja pomocnicza do odbierania wyników i aktualizacji paska postępu
def collect_results(results):
	for line in results:
		q.put(line)
	pbar.update()

# Start multiprocessing
with mp.Pool(PROCESSES) as pool:
	for _ in pool.imap_unordered(compute_pair_task, pairs, chunksize=10):
		collect_results(_)

# Finalizacja
pbar.close()
stop_event.set()
writer.join()

print('\a', end='', file=sys.stderr)
