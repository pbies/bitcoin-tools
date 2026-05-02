#!/usr/bin/env python3

import sys
import threading
import hashlib
import base58
import argparse
from coincurve import PublicKey

TARGET = "1HZNsUqQxKVLmfPfCAzLwrnVDzx8CxwxnM"
START = 0xbff0796c4e43477be6a17216e403d06c5c20ec1eae13a9d086478eca00000000
END = 0xbff0796c4e43477be6a17216e403d06c5c20ec1eae13a9d086478ecaffffffff
THREADS = 30
FOUND = threading.Event()
LOCK = threading.Lock()
COUNTER = [0]

def sha256(data):
	return hashlib.sha256(data).digest()

def ripemd160(data):
	h = hashlib.new("ripemd160")
	h.update(data)
	return h.digest()

def hash160(data):
	return ripemd160(sha256(data))

def privkey_to_p2pkh(privkey_int, compressed=True):
	key_bytes = privkey_int.to_bytes(32, "big")
	pub = PublicKey.from_valid_secret(key_bytes)
	if compressed:
		pub_bytes = pub.format(compressed=True)
	else:
		pub_bytes = pub.format(compressed=False)
	h160 = hash160(pub_bytes)
	# version byte 0x00 for mainnet P2PKH
	payload = b"\x00" + h160
	checksum = sha256(sha256(payload))[:4]
	return base58.b58encode(payload + checksum).decode()

def worker(start, end, thread_id):
	global COUNTER
	local_count = 0
	i = start
	while i <= end and not FOUND.is_set():
		addr_c = privkey_to_p2pkh(i, compressed=True)
		if addr_c == TARGET:
			with LOCK:
				print(f"\n[FOUND] compressed")
				print(f"privkey: {hex(i)}")
				print(f"address: {addr_c}")
			FOUND.set()
			return
		addr_u = privkey_to_p2pkh(i, compressed=False)
		if addr_u == TARGET:
			with LOCK:
				print(f"\n[FOUND] uncompressed")
				print(f"privkey: {hex(i)}")
				print(f"address: {addr_u}")
			FOUND.set()
			return
		i += 1
		local_count += 1
		if local_count % 1000 == 0:
			with LOCK:
				COUNTER[0] += 1000
				sys.stdout.write(f"\rkeys checked: {COUNTER[0]:,}  thread {thread_id} @ {hex(i)}")
				sys.stdout.flush()
			local_count = 0

	with LOCK:
		COUNTER[0] += local_count

def main():
	global TARGET, START, END, THREADS

	parser = argparse.ArgumentParser(description="Multithreaded P2PKH private key range scanner")
	parser.add_argument("--target", required=True, help="Target P2PKH address (1...)")
	parser.add_argument("--start", required=True, help="Start of range (hex, e.g. 0x1)")
	parser.add_argument("--end", required=True, help="End of range (hex, e.g. 0xffffff)")
	parser.add_argument("--threads", type=int, default=4, help="Thread count (default: 4)")
	args = parser.parse_args()

	TARGET = args.target
	START = int(args.start, 16)
	END = int(args.end, 16)
	THREADS = args.threads

	if not TARGET.startswith("1"):
		print("ERROR: target must be a P2PKH address starting with 1")
		sys.exit(1)

	if START > END:
		print("ERROR: start > end")
		sys.exit(1)

	total = END - START + 1
	chunk = total // THREADS
	print(f"target:  {TARGET}")
	print(f"range:   {hex(START)} - {hex(END)}")
	print(f"total:   {total:,} keys")
	print(f"threads: {THREADS}")
	print()

	threads = []
	for t in range(THREADS):
		t_start = START + t * chunk
		t_end = t_start + chunk - 1 if t < THREADS - 1 else END
		th = threading.Thread(target=worker, args=(t_start, t_end, t), daemon=True)
		threads.append(th)
		th.start()

	for th in threads:
		th.join()

	print()
	if not FOUND.is_set():
		print(f"not found. keys checked: {COUNTER[0]:,}")

if __name__ == "__main__":
	main()
