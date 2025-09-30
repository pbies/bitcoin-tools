#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from tqdm import tqdm
import sys, base58, os
import threading
import queue

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(i, j, q):
	for z in [-65536, -65535, -31337, -1000, -100, -64, 0, 1, 64, 100, 1000, 31337, 65535, 65536]:
		y = (i**j) % (2**256)
		h = hex(y + z)[2:].zfill(64)
		try:
			hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=h)
		except:
			continue
		wif = pvk_to_wif2(h)
		a = f'{h}\n{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
		q.put(a)

def writer_thread(q, stop_event):
	with open('output.txt', 'w') as f:
		while not stop_event.is_set() or not q.empty():
			try:
				data = q.get(timeout=0.1)
				f.write(data)
				f.flush()
			except queue.Empty:
				continue

def worker_loop(i_values, j_values, q):
	for i in i_values:
		for j in j_values:
			go(i, j, q)

# Main execution
os.system('cls' if os.name == 'nt' else 'clear')

q = queue.Queue()
stop_event = threading.Event()

# Start writer thread
writer = threading.Thread(target=writer_thread, args=(q, stop_event))
writer.start()

# Divide the workload among worker threads
num_threads = 30
i_range = list(range(2, 1025))
j_range = list(range(2, 1025))
chunk_size = len(i_range) // num_threads
threads = []

for n in range(num_threads):
	i_chunk = i_range[n*chunk_size : (n+1)*chunk_size] if n < num_threads - 1 else i_range[n*chunk_size:]
	t = threading.Thread(target=worker_loop, args=(i_chunk, j_range, q))
	t.start()
	threads.append(t)

# Progress bar in main thread (optional)
for t in threads:
	t.join()

# Signal the writer to finish and wait
stop_event.set()
writer.join()

print('\a', end='', file=sys.stderr)
