#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.entropies import BIP39Entropy
from hdwallet.hds import BIP32HD
from tqdm import tqdm
import queue
import sys, base58, os
import threading
import time

# Funkcja konwertująca hex na WIF
def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

# Robota dla jednej pary (i, j)
def compute_pair(i, j, q, counter, lock):
	base = pow(i, j, 1<<128)  # oblicz tylko raz
	for z in OFFSETS:
		hval = (base + z) % (1<<128)
		h = hex(hval)[2:].zfill(32)
		try:
			hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_entropy(entropy=BIP39Entropy(h))
		except:
			continue
		# Można skrócić, np. tylko P2PKH
		a = f'{h}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
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
OFFSETS = [-65536, -65535, -31337, -1000, -100, -64, 0, 1, 64, 100, 1000, 31337, 65535, 65536]
THREADS = 4

# Czyszczenie terminala
os.system('cls||clear')

# Zakresy do przetworzenia
i_range = list(range(2, 129))
j_range = list(range(2, 129))
total = len(i_range) * len(j_range)

# Kolejka i synchronizacja
q = queue.Queue()
counter = [0]
lock = threading.Lock()
stop_event = threading.Event()

# Pasek postępu
pbar = tqdm(total=total, desc="Progress", unit="pair")

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
