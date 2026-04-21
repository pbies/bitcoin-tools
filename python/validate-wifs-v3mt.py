#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading
import sys
import os

WORKERS = os.cpu_count() or 4

_local = threading.local()
_lock = threading.Lock()

def get_wallet():
	if not hasattr(_local, 'wallet'):
		_local.wallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	return _local.wallet

def validate(k):
	try:
		get_wallet().from_wif(wif=k)
		return k, True
	except Exception:
		return k, False

def main():
	with open('wifs.txt', 'r') as f:
		print('Reading...', flush=True)
		lines = f.read().splitlines()

	good_buf = []
	bad_buf = []
	FLUSH_EVERY = 1000

	def flush(good_f, bad_f, force=False):
		if force or len(good_buf) >= FLUSH_EVERY:
			good_f.write('\n'.join(good_buf) + ('\n' if good_buf else ''))
			good_f.flush()
			good_buf.clear()
		if force or len(bad_buf) >= FLUSH_EVERY:
			bad_f.write('\n'.join(bad_buf) + ('\n' if bad_buf else ''))
			bad_f.flush()
			bad_buf.clear()

	print(f'Validating with {WORKERS} threads...', flush=True)

	with open('wifs-good.txt', 'w') as good_f, open('wifs-bad.txt', 'w') as bad_f:
		with ThreadPoolExecutor(max_workers=WORKERS) as executor:
			futures = {executor.submit(validate, k): k for k in lines}
			with tqdm(total=len(lines)) as bar:
				for future in as_completed(futures):
					k, ok = future.result()
					with _lock:
						if ok:
							good_buf.append(k)
						else:
							bad_buf.append(k)
						flush(good_f, bad_f)
					bar.update(1)
		with _lock:
			flush(good_f, bad_f, force=True)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
