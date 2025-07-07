#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from tqdm import tqdm
import sys, base58, os
import threading
import queue
import time

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

cnst=1<<256

def go(i, j, q, counter, lock):
	y = (i**j) % cnst
	for z in [-65536, -65535, -31337, -1000, -100, -64, 0, 1, 64, 100, 1000, 31337, 65535, 65536]:
		h = hex(y + z)[2:].zfill(64)
		try:
			hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=h)
		except:
			continue
		wif = pvk_to_wif2(h)
		a = f'{h}\n{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
		q.put(a)
	# Increment counter
	with lock:
		counter[0] += 1

def writer_thread(q, stop_event):
	with open('output.txt', 'w') as f:
		while not stop_event.is_set() or not q.empty():
			try:
				data = q.get(timeout=0.1)
				f.write(data)
				f.flush()
			except queue.Empty:
				continue

def worker_loop(i_values, j_values, q, counter, lock):
	for i in i_values:
		for j in j_values:
			go(i, j, q, counter, lock)

# Main execution
os.system('cls||clear')

q = queue.Queue()
stop_event = threading.Event()
counter = [0]
counter_lock = threading.Lock()

# Oblicz całkowitą liczbę iteracji (i * j)
i_range = list(range(2, 1025))
j_range = list(range(2, 1025))
total_iterations = len(i_range) * len(j_range)

# Pasek postępu
progress_bar = tqdm(total=total_iterations, desc="Progress", unit="pair")

# Wątek zapisujący
writer = threading.Thread(target=writer_thread, args=(q, stop_event))
writer.start()

# Podział pracy
num_threads = 30
chunk_size = len(i_range) // num_threads
threads = []

for n in range(num_threads):
	i_chunk = i_range[n*chunk_size : (n+1)*chunk_size] if n < num_threads - 1 else i_range[n*chunk_size:]
	t = threading.Thread(target=worker_loop, args=(i_chunk, j_range, q, counter, counter_lock))
	t.start()
	threads.append(t)

# Aktualizacja postępu w głównym wątku
while any(t.is_alive() for t in threads):
	with counter_lock:
		progress_bar.n = counter[0]
		progress_bar.refresh()
	time.sleep(0.1)

# Final update
with counter_lock:
	progress_bar.n = counter[0]
	progress_bar.refresh()
progress_bar.close()

# Czekaj na wątki
for t in threads:
	t.join()

stop_event.set()
writer.join()

print('\a', end='', file=sys.stderr)
