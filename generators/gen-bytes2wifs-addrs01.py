#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List
import argparse
import sys, os, base58, hashlib

# Optional imports for platform-specific short critical-section locking
_IS_WIN = os.name == "nt"
if _IS_WIN:
	import msvcrt
else:
	import fcntl

# NOTE: user prefers tabs for indentation
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex: str) -> str:
	# uncompressed WIF (prefix 0x80 + 32B privkey)
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def _lock_file(f):
	# Acquire a short exclusive lock just for the write critical section
	if _IS_WIN:
		try:
			msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
		except OSError:
			msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
	else:
		fcntl.flock(f.fileno(), fcntl.LOCK_EX)

def _unlock_file(f):
	if _IS_WIN:
		try:
			msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
		except OSError:
			pass
	else:
		fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def _sha256_hex(b: bytes) -> str:
	return hashlib.sha256(b).hexdigest()

def int_to_bytes3(value: int, length: int | None = None) -> bytes:
	if value == 0 and not length:
		return b"\x00"
	if not length:
		length = (value.bit_length() + 7) // 8 or 1
	return value.to_bytes(length, "big")

def _gen_privkey_hex_from_1_to_4_bytes(count) -> str:
	for i in range(0, count):
		yield i

def process_one(i) -> Optional[str]:
	# _: dummy index for Pool map
	b=int_to_bytes3(i)
	s=_sha256_hex(b)
	key_hex = s.zfill(64)
	try:
		hdwallet.from_private_key(private_key=key_hex)
	except Exception:
		return None

	wif = pvk_to_wif2(key_hex)
	a = (
		f"{key_hex}\n"
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
	return a

def write_results(results: Iterable[str], out_path: Path, fsync: bool = True) -> None:
	if not results:
		return
	out_path.parent.mkdir(parents=True, exist_ok=True)
	while True:
		try:
			with out_path.open('a', encoding='utf-8', buffering=1) as f:
				_lock_file(f)
				try:
					for r in results:
						if r is not None:
							f.write(r)
					f.flush()
					if fsync:
						os.fsync(f.fileno())
				finally:
					_unlock_file(f)
					return
		except:
			pass

def _pool_worker_init():
	# każdy proces ma własny HDWallet (żeby nie współdzielić stanu)
	global hdwallet
	try:
		from hdwallet import HDWallet
		from hdwallet.cryptocurrencies import Bitcoin as BTC
		from hdwallet.hds import BIP32HD
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	except Exception:
		hdwallet = None

def main():
	parser = argparse.ArgumentParser(description="Generate privkeys as sha256(random 1..4 bytes), then output WIF + addresses")
	parser.add_argument('-o','--output', type=str, default='output.txt', help='output file path')
	parser.add_argument('-w','--workers', type=int, default=24, help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c','--chunk', type=int, default=10000, help='results per write chunk')
	parser.add_argument('-n','--count', type=int, default=2**24, help='how many keys to generate')
	parser.add_argument('--min-bytes', type=int, default=1, help='min random bytes before sha256 (default 1)')
	parser.add_argument('--max-bytes', type=int, default=4, help='max random bytes before sha256 (default 4)')
	parser.add_argument('--no-fsync', action='store_true', help='disable fsync() after each chunk to improve speed')
	args = parser.parse_args()

	out_path = Path(args.output)
	count = args.count

	# Truncate/create output file once
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open('w', encoding='utf-8') as f:
		pass

	pbar = tqdm(
		total=count,
		unit='key',
		ncols=132
	)

	workers = args.workers

	if workers == 1:
		buf: List[str] = []
		for i in range(count):
			r = process_one(i)
			if r is not None:
				buf.append(r)
			if len(buf) >= args.chunk:
				write_results(buf, out_path, fsync=not args.no_fsync)
				buf.clear()
			pbar.update(1)
		if buf:
			write_results(buf, out_path, fsync=not args.no_fsync)
	else:
		with Pool(processes=workers, initializer=_pool_worker_init) as pool:
			buf: List[str] = []
			# imap_unordered zmniejsza narzut i poprawia płynność
			for r in pool.imap_unordered(
				process_one,
				_gen_privkey_hex_from_1_to_4_bytes(count),
				chunksize=1000
			):
				if r is not None:
					buf.append(r)
				if len(buf) >= args.chunk:
					write_results(buf, out_path, fsync=not args.no_fsync)
					buf.clear()
				pbar.update(1)
			if buf:
				write_results(buf, out_path, fsync=not args.no_fsync)

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
