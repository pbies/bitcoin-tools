#!/usr/bin/env python3

import sys
import hashlib
import argparse
import multiprocessing as mp
from coincurve import PublicKey
import base58

REPORT_INTERVAL = 10_000

def sha256d(data):
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def hash160(data):
	h = hashlib.new("ripemd160")
	h.update(hashlib.sha256(data).digest())
	return h.digest()

def scan_chunk(args):
	start, end, target = args
	for i in range(start, end + 1):
		key_bytes = i.to_bytes(32, "big")
		pub = PublicKey.from_valid_secret(key_bytes)
		for compressed in (True, False):
			pub_bytes = pub.format(compressed=compressed)
			h160 = hash160(pub_bytes)
			payload = b"\x00" + h160
			checksum = sha256d(payload)[:4]
			addr = base58.b58encode(payload + checksum).decode()
			if addr == target:
				return ("found", i, compressed, addr)
		if (i - start) % REPORT_INTERVAL == 0 and i != start:
			return ("progress", i, REPORT_INTERVAL, start)
	return ("done", end - start + 1, start)

def sha256d(data):
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def split_range(start, end, chunk_size):
	chunks = []
	i = start
	while i <= end:
		chunk_end = min(i + chunk_size - 1, end)
		chunks.append((i, chunk_end))
		i = chunk_end + 1
	return chunks

def main():
	parser = argparse.ArgumentParser(description="Multiprocessing P2PKH key range scanner")
	parser.add_argument("--target", required=True, help="Target P2PKH address (starts with 1)")
	parser.add_argument("--start", required=True, help="Start of range (hex)")
	parser.add_argument("--end", required=True, help="End of range (hex)")
	parser.add_argument("--workers", type=int, default=mp.cpu_count(), help="Worker process count")
	parser.add_argument("--chunk", type=int, default=50_000, help="Keys per task chunk")
	args = parser.parse_args()

	if not args.target.startswith("1"):
		print("ERROR: target must be P2PKH (starts with 1)")
		sys.exit(1)

	start = int(args.start, 16)
	end = int(args.end, 16)
	if start > end:
		print("ERROR: start > end")
		sys.exit(1)

	target = args.target
	total = end - start + 1
	tasks = [(s, e, target) for s, e in split_range(start, end, args.chunk)]

	print(f"target:  {target}")
	print(f"range:   {hex(start)} - {hex(end)}")
	print(f"total:   {total:,} keys  ({len(tasks)} chunks)")
	print(f"workers: {args.workers}")
	print()

	checked = 0

	with mp.Pool(processes=args.workers) as pool:
		for result in pool.imap_unordered(scan_chunk, tasks):
			status = result[0]
			if status == "found":
				_, privkey_int, compressed, addr = result
				pool.terminate()
				print(f"\n[FOUND]")
				print(f"privkey:    {hex(privkey_int)}")
				print(f"compressed: {compressed}")
				print(f"address:    {addr}")
				return
			elif status == "progress":
				_, current, interval, chunk_start = result
				checked += interval
				sys.stdout.write(f"\rchecked: {checked:,}  current: {hex(current)}")
				sys.stdout.flush()
			elif status == "done":
				_, chunk_total, chunk_start = result
				checked += chunk_total
				sys.stdout.write(f"\rchecked: {checked:,}")
				sys.stdout.flush()

	print(f"\nnot found. total checked: {checked:,}")

if __name__ == "__main__":
	main()
