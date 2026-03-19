#!/usr/bin/env python3

import os
import base58
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

CHUNK_SIZE	  = 32
NUM_WORKERS	 = os.cpu_count() or 4
QUEUE_MAXSIZE   = NUM_WORKERS * 256   # bound memory usage
PROGRESS_EVERY  = 10 * 1024		   # print progress every 10 KB
SENTINEL		= None				# signals writer thread to stop


def read_binary_chunks(filepath, chunk_size=CHUNK_SIZE):
	"""Yield (pos, file_size, chunk) sliding one byte at a time, streaming."""
	file_size = os.path.getsize(filepath)
	buf = bytearray()
	with open(filepath, 'rb') as f:
		pos = 0
		while True:
			needed = chunk_size - len(buf)
			if needed > 0:
				data = f.read(needed)
				if not data:
					break
				buf.extend(data)
			if len(buf) < chunk_size:
				break
			yield pos, file_size, bytes(buf[:chunk_size])
			buf = buf[1:]
			pos += 1


def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


def process_chunk(key_hex: str):
	"""
	Run in a worker thread. Each thread gets its own HDWallet instance
	(hdwallet objects are not thread-safe).
	Returns a result string on success, None on any error.
	"""
	hw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	try:
		hw.from_private_key(private_key=key_hex)
	except Exception:
		return None, "hd"

	try:
		wif = pvk_to_wif2(key_hex)
	except Exception:
		return None, "wif"

	result = (
		f"{key_hex}\n"
		f"{wif}\n"
		f"{hw.wif()}\n"
		f"{hw.address('P2PKH')}\n"
		f"{hw.address('P2SH')}\n"
		f"{hw.address('P2TR')}\n"
		f"{hw.address('P2WPKH')}\n"
		f"{hw.address('P2WPKH-In-P2SH')}\n"
		f"{hw.address('P2WSH')}\n"
		f"{hw.address('P2WSH-In-P2SH')}\n\n"
	)
	return result, None


def writer_thread(write_queue, out_path, counters, counters_lock):
	"""Dedicated thread that drains the write queue and writes to disk."""
	with open(out_path, 'w') as f:
		while True:
			item = write_queue.get()
			if item is SENTINEL:
				break
			f.write(item)
			with counters_lock:
				counters['written'] += 1


if __name__ == "__main__":
	inp = "input.dat"
	out = "output.txt"

	counters = {'total': 0, 'hd_err': 0, 'wif_err': 0, 'written': 0}
	counters_lock = threading.Lock()
	write_queue   = queue.Queue(maxsize=QUEUE_MAXSIZE)

	# Start dedicated writer thread
	wt = threading.Thread(
		target=writer_thread,
		args=(write_queue, out, counters, counters_lock),
		daemon=True,
	)
	wt.start()

	last_progress_pos = -PROGRESS_EVERY

	def submit(pos_file_chunk):
		pos, file_size, chunk = pos_file_chunk
		key_hex = chunk.hex()
		result, err = process_chunk(key_hex)

		with counters_lock:
			counters['total'] += 1
			if err == 'hd':
				counters['hd_err'] += 1
			elif err == 'wif':
				counters['wif_err'] += 1

		if result:
			write_queue.put(result)   # blocks if queue is full (backpressure)

	with ThreadPoolExecutor(max_workers=NUM_WORKERS) as pool:
		for pos, file_size, chunk in read_binary_chunks(inp):
			# Progress printed by the main thread (reader), every 10 KB
			if pos - last_progress_pos >= PROGRESS_EVERY:
				pct = pos / file_size * 100 if file_size else 0
				with counters_lock:
					w  = counters['written']
					he = counters['hd_err']
					we = counters['wif_err']
				print(
					f"\r[{pos:,} / {file_size:,} bytes  {pct:.2f}%"
					f"  written={w}  hd_err={he}  wif_err={we}]",
					end='', flush=True,
				)
				last_progress_pos = pos

			pool.submit(submit, (pos, file_size, chunk))

	# All futures done — signal writer to finish and wait
	write_queue.put(SENTINEL)
	wt.join()

	print()
	print(f"\nSummary:")
	print(f"  Workers				: {NUM_WORKERS}")
	print(f"  Total chunks processed : {counters['total']:,}")
	print(f"  Written				: {counters['written']:,}")
	print(f"  Skipped (hdwallet err) : {counters['hd_err']:,}")
	print(f"  Skipped (wif err)	  : {counters['wif_err']:,}")
