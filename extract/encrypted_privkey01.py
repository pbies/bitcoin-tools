#!/usr/bin/env python3

import json
import sys
import hashlib
import threading
from queue import Queue
from Crypto.Cipher import AES

def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int, iv_len: int):
	d = b''
	d_i = b''
	while len(d) < key_len + iv_len:
		d_i = hashlib.md5(d_i + password + salt).digest()
		d += d_i
	return d[:key_len], d[key_len:key_len + iv_len]

def try_decrypt(encrypted_hex: str, password: str, expected_secret: str) -> bool:
	try:
		enc = bytes.fromhex(encrypted_hex.replace(' ', ''))
		# OpenSSL format: "Salted__" + 8-byte salt + ciphertext
		# Bitcoin Core does NOT use salted format - it uses a fixed derivation
		# The key is derived: SHA512(passphrase + salt) iterated
		# Actually Bitcoin Core uses Cryptoer: AES-256-CBC, key = SHA512(passphrase)[0:32], iv = SHA512(passphrase)[32:48]
		# More precisely: key derived via 25000x SHA512 stretch
		pass_bytes = password.encode('utf-8')
		# Bitcoin Core key derivation: EVP_BytesToKey with no salt, 1 iteration for older wallets
		# But actual Bitcoin Core uses: key = first 32 bytes of SHA512(password), iv = next 16 bytes
		# This is for wallet encryption per src/wallet/crypter.cpp
		digest = hashlib.sha512(pass_bytes).digest()
		# Iterated: Bitcoin Core does 25000 rounds
		for _ in range(25000 - 1):
			digest = hashlib.sha512(digest).digest()
		key = digest[:32]
		iv  = digest[32:48]
		cipher = AES.new(key, AES.MODE_CBC, iv)
		decrypted = cipher.decrypt(enc)
		# Strip PKCS7 padding
		pad = decrypted[-1]
		if pad < 1 or pad > 16:
			return False
		decrypted = decrypted[:-pad]
		result_hex = decrypted.hex()
		# secret field is hexsec + '01' for compressed
		if result_hex == expected_secret:
			return True
		return False
	except Exception:
		return False

def worker(queue: Queue, keys: list, result_holder: list, lock: threading.Lock, stop_event: threading.Event):
	while not stop_event.is_set():
		try:
			password = queue.get(timeout=0.2)
		except Exception:
			continue
		for k in keys:
			enc = k['encrypted_privkey']
			secret = k['secret']
			if try_decrypt(enc, password, secret):
				with lock:
					result_holder.append(password)
					stop_event.set()
				queue.task_done()
				return
		queue.task_done()

def main():
	if len(sys.argv) < 3:
		print(f"Usage: {sys.argv[0]} <wallet_dump.json> <wordlist.txt> [threads]")
		sys.exit(1)

	json_file  = sys.argv[1]
	wordlist   = sys.argv[2]
	num_threads = int(sys.argv[3]) if len(sys.argv) > 3 else 8

	with open(json_file, 'r') as f:
		data = json.load(f)

	# Collect all entries that have encrypted_privkey + secret
	keys = [
		{'encrypted_privkey': k['encrypted_privkey'], 'secret': k['secret']}
		for k in data.get('keys', [])
		if 'encrypted_privkey' in k and 'secret' in k
	]

	if not keys:
		print("No encrypted keys found in JSON.")
		sys.exit(1)

	print(f"Loaded {len(keys)} encrypted key(s). Starting brute-force with {num_threads} threads.")

	q = Queue(maxsize=num_threads * 4)
	result_holder = []
	lock = threading.Lock()
	stop_event = threading.Event()

	threads = []
	for _ in range(num_threads):
		t = threading.Thread(target=worker, args=(q, keys, result_holder, lock, stop_event), daemon=True)
		t.start()
		threads.append(t)

	tried = 0
	with open(wordlist, 'r', errors='replace') as f:
		for line in f:
			if stop_event.is_set():
				break
			pw = line.rstrip('\n')
			q.put(pw)
			tried += 1
			if tried % 1000 == 0:
				print(f"\rTried: {tried}", end='', flush=True)

	q.join()
	stop_event.set()

	for t in threads:
		t.join()

	print()
	if result_holder:
		print(f"Password found: {result_holder[0]}")
	else:
		print(f"Password not found. Tried {tried} candidates.")

if __name__ == '__main__':
	main()
