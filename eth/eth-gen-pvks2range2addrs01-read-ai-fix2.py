#!/usr/bin/env python3

# very slow

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from tqdm import tqdm
import sys, base58, os
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import time
from Crypto.Hash import keccak
from ecpy.curves import Curve
from web3 import Web3

# Funkcja konwertująca hex na WIF
def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

# Robota dla jednej pary (i, j)
def compute_pair(i, j, q, counter, lock):
	base = (i**j)%(1<<256)
	for z in OFFSETS:
		private_key = (base + z)
		if private_key<1:
			continue

		cv = Curve.get_curve('secp256k1')
		try:
			pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)
			concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
		except:
			return

		k=keccak.new(digest_bits=256)
		k.update(concat_x_y)
		eth_addr = '0x' + k.hexdigest()[-40:]

		cksum=Web3.to_checksum_address(eth_addr)
		p=hex(private_key)[2:].zfill(64)
		a=f'{cksum} {p}\n'
		q.put(a)
	# Aktualizacja licznika
	with lock:
		counter[0] += 1

# Wątek zapisujący dane z kolejki do pliku
def writer_thread(q, stop_event):
	with open('output.txt', 'w', buffering=1) as f:  # linia buforowa
		while not stop_event.is_set() or not q.empty():
			try:
				data = q.get(timeout=0.1)
				f.write(data)
			except queue.Empty:
				continue

# Parametry i stałe
OFFSETS = [-65536, -65535, -31337, -1024, -1000, -100, -64, -2, -1, 0, 1, 2, 64, 100, 1000, 1024, 31337, 65535, 65536]
THREADS = 30

# Czyszczenie terminala
os.system('cls' if os.name == 'nt' else 'clear')

# Zakresy do przetworzenia
i_range = list(range(2, 256))
j_range = list(range(2, 2049))
total = len(i_range) * len(j_range)

# Kolejka i synchronizacja
q = queue.Queue()
counter = [0]
lock = threading.Lock()
stop_event = threading.Event()

# Pasek postępu
pbar = tqdm(total=total)

# Start wątku zapisującego
writer = threading.Thread(target=writer_thread, args=(q, stop_event))
writer.start()

# Start obliczeń w ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=THREADS) as executor:
	futures = []
	for i in i_range:
		for j in j_range:
			futures.append(executor.submit(compute_pair, i, j, q, counter, lock))

	# Aktualizacja paska postępu w tle
	while any(f.done() is False for f in futures):
		with lock:
			pbar.n = counter[0]
			pbar.refresh()
		time.sleep(0.1)

# Finalizacja
with lock:
	pbar.n = counter[0]
	pbar.refresh()
pbar.close()

# Kończymy zapis
stop_event.set()
writer.join()

print('\a', end='', file=sys.stderr)
