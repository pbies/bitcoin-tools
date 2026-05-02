#!/usr/bin/env python3
# wallet_extract.py
# Extract ckeys and private keys from Bitcoin Core wallet.dat (BerkeleyDB binary, unencrypted)
# No bsddb3 dependency — pure binary scan with BDB page parsing

import sys
import os
import struct
import hashlib
import binascii
from pathlib import Path

# BerkeleyDB page types
BDB_PAGE_BTREE_LEAF = 5
BDB_PAGE_SIZE_DEFAULT = 4096

# Known wallet.dat key prefixes (length-prefixed strings in BDB records)
KEY_PREFIX_CKEY   = b'\x04ckey'     # compressed public key + encrypted private key
KEY_PREFIX_KEY    = b'\x03key'      # uncompressed pubkey entry
KEY_PREFIX_WKEY   = b'\x04wkey'     # wallet key (older format)
KEY_PREFIX_MKEY   = b'\x04mkey'     # master key (encrypted wallets)

# Unencrypted private key record: key=\x03key<pubkey>, value=<privkey_payload>
# ckey record: key=\x04ckey<pubkey>, value=<encrypted_privkey>

def read_varint(data, offset):
	"""Bitcoin-style varint (also used in BDB wallet key serialization)."""
	b = data[offset]
	if b < 0xfd:
		return b, offset + 1
	elif b == 0xfd:
		return struct.unpack_from('<H', data, offset + 1)[0], offset + 3
	elif b == 0xfe:
		return struct.unpack_from('<I', data, offset + 1)[0], offset + 5
	else:
		return struct.unpack_from('<Q', data, offset + 1)[0], offset + 9

def decode_privkey_payload(payload):
	"""
	Wallet private key payload is a serialized CPrivKey.
	Format: varint(len) + raw_privkey_bytes (32 bytes for secp256k1)
	Sometimes prefixed with DER-encoded key — try both approaches.
	"""
	if len(payload) < 32:
		return None

	# Try direct: first 32 bytes
	candidate = payload[:32]
	if len(payload) >= 33:
		# varint prefix variant
		try:
			length, off = read_varint(payload, 0)
			if off + length <= len(payload) and length in (32, 33, 279, 214):
				raw = payload[off:off + length]
				# DER-encoded key starts with 0x30 — extract scalar
				if raw[0] == 0x30 and length > 32:
					return extract_privkey_from_der(raw)
				if length == 32:
					return raw
				if length == 33 and raw[0] in (0x01,):
					return raw[1:33]
		except Exception:
			pass

	# Fallback: scan for 32-byte scalar
	# Many wallet records store: <1-byte flag><32-byte key> or just 32 bytes
	for start in range(0, min(4, len(payload) - 31)):
		chunk = payload[start:start + 32]
		val = int.from_bytes(chunk, 'big')
		if 0 < val < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141:
			return chunk

	return None

def extract_privkey_from_der(der):
	"""Extract 32-byte private key scalar from DER-encoded ECPrivateKey (SEC1)."""
	# SEC1 ECPrivateKey: 30 len 02 01 01 04 20 <32 bytes> ...
	try:
		i = 0
		if der[i] != 0x30:
			return None
		i += 1
		# skip length
		if der[i] & 0x80:
			llen = der[i] & 0x7f
			i += 1 + llen
		else:
			i += 1
		# version: INTEGER 1
		if der[i] == 0x02:
			i += 1
			vlen = der[i]; i += 1
			i += vlen
		# private key: OCTET STRING
		if i < len(der) and der[i] == 0x04:
			i += 1
			klen = der[i]; i += 1
			if klen >= 32:
				return der[i:i + 32]
	except (IndexError, TypeError):
		pass
	return None

def pubkey_to_address(pubkey_bytes):
	"""P2PKH address from raw pubkey bytes."""
	import hashlib
	sha256 = hashlib.sha256(pubkey_bytes).digest()
	ripemd = hashlib.new('ripemd160', sha256).digest()
	versioned = b'\x00' + ripemd
	checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
	payload = versioned + checksum
	# base58
	alphabet = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	n = int.from_bytes(payload, 'big')
	result = []
	while n > 0:
		n, rem = divmod(n, 58)
		result.append(alphabet[rem:rem + 1])
	for byte in payload:
		if byte == 0:
			result.append(alphabet[0:1])
		else:
			break
	return b''.join(reversed(result)).decode()

def privkey_to_wif(privkey_bytes, compressed=True):
	"""Convert 32-byte private key to WIF."""
	prefix = b'\x80'
	payload = prefix + privkey_bytes
	if compressed:
		payload += b'\x01'
	checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
	full = payload + checksum
	alphabet = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	n = int.from_bytes(full, 'big')
	result = []
	while n > 0:
		n, rem = divmod(n, 58)
		result.append(alphabet[rem:rem + 1])
	for byte in full:
		if byte == 0:
			result.append(alphabet[0:1])
		else:
			break
	return b''.join(reversed(result)).decode()

def scan_bdb_pages(data):
	"""
	Parse BerkeleyDB B-tree pages.
	BDB page header (36 bytes):
	  0x00: LSN (8)
	  0x08: pgno (4)
	  0x0C: prev_pgno (4)
	  0x10: next_pgno (4)
	  0x14: entries (2)  — number of items on page
	  0x16: hf_offset (2) — high free byte offset
	  0x18: level (1)
	  0x19: type (1)
	  0x1A: unused (22) — varies by version
	Page size auto-detected from metadata page.
	"""
	results = []
	if len(data) < 4096:
		return results

	# Page 0 is metadata; page size at offset 20 (uint32 LE)
	try:
		page_size = struct.unpack_from('<I', data, 20)[0]
		if page_size not in (512, 1024, 2048, 4096, 8192, 16384, 32768, 65536):
			page_size = BDB_PAGE_SIZE_DEFAULT
	except Exception:
		page_size = BDB_PAGE_SIZE_DEFAULT

	total_pages = len(data) // page_size
	for pgno in range(1, total_pages):
		offset = pgno * page_size
		if offset + 26 > len(data):
			break
		page_type = data[offset + 25]
		if page_type != BDB_PAGE_BTREE_LEAF:
			continue
		try:
			entries = struct.unpack_from('<H', data, offset + 20)[0]
			# Item offsets start at byte 26 on page, each is uint16 LE
			# Items alternate: key, value, key, value ...
			item_offsets = []
			for i in range(entries):
				item_off = struct.unpack_from('<H', data, offset + 26 + i * 2)[0]
				item_offsets.append(item_off)

			for i in range(0, len(item_offsets) - 1, 2):
				k_off = offset + item_offsets[i]
				v_off = offset + item_offsets[i + 1]

				# Each item: type(1) + pad(1) + len(2) + data
				if k_off + 4 > len(data) or v_off + 4 > len(data):
					continue
				k_len = struct.unpack_from('<H', data, k_off + 2)[0]
				v_len = struct.unpack_from('<H', data, v_off + 2)[0]
				if k_len == 0 or v_len == 0:
					continue
				if k_off + 4 + k_len > len(data) or v_off + 4 + v_len > len(data):
					continue

				k_data = data[k_off + 4: k_off + 4 + k_len]
				v_data = data[v_off + 4: v_off + 4 + v_len]
				results.append((k_data, v_data))
		except (struct.error, IndexError):
			continue

	return results

def brute_scan(data):
	"""
	Fallback: byte-level scan for key/ckey prefix patterns.
	Used when BDB page parsing yields nothing (corruption, unknown format).
	Looks for length-prefixed strings matching wallet key names.
	"""
	results = []
	i = 0
	length = len(data)

	while i < length - 6:
		# \x03key or \x04ckey
		b = data[i]
		if b == 0x03 and data[i+1:i+4] == b'key':
			k_data = data[i:i + 4]
			# pubkey follows: 33 or 65 bytes
			for pk_len in (33, 65):
				if i + 4 + pk_len < length:
					pk = data[i + 4: i + 4 + pk_len]
					if pk[0] in (0x02, 0x03, 0x04):
						# value is somewhere nearby — can't reliably extract without BDB structure
						results.append(('key_raw', pk, None))
						break
			i += 4
			continue

		if b == 0x04 and data[i+1:i+5] == b'ckey':
			k_data = data[i:i + 5]
			for pk_len in (33, 65):
				if i + 5 + pk_len < length:
					pk = data[i + 5: i + 5 + pk_len]
					if pk[0] in (0x02, 0x03, 0x04):
						results.append(('ckey_raw', pk, None))
						break
			i += 5
			continue

		i += 1

	return results

def process_records(records):
	keys = []  # list of dicts

	for k_data, v_data in records:
		# Determine record type from key prefix
		if len(k_data) < 4:
			continue

		rec_type = None
		pubkey = None

		# key record: \x03key + pubkey (33 or 65 bytes)
		if k_data[0] == 0x03 and k_data[1:4] == b'key':
			rec_type = 'key'
			pubkey = k_data[4:]

		# ckey record: \x04ckey + pubkey
		elif k_data[0] == 0x04 and k_data[1:5] == b'ckey':
			rec_type = 'ckey'
			pubkey = k_data[5:]

		# wkey record: \x04wkey + pubkey
		elif k_data[0] == 0x04 and k_data[1:5] == b'wkey':
			rec_type = 'wkey'
			pubkey = k_data[5:]

		# mkey: master key for encrypted wallet
		elif k_data[0] == 0x04 and k_data[1:5] == b'mkey':
			rec_type = 'mkey'

		if rec_type == 'mkey':
			keys.append({
				'type': 'mkey',
				'note': 'wallet is encrypted — master key record found, passphrase required',
				'raw_value_hex': v_data.hex(),
			})
			continue

		if rec_type in ('key', 'wkey') and pubkey:
			privkey = decode_privkey_payload(v_data)
			compressed = len(pubkey) == 33
			entry = {
				'type': rec_type,
				'pubkey_hex': pubkey.hex(),
				'privkey_hex': privkey.hex() if privkey else None,
				'wif': privkey_to_wif(privkey, compressed) if privkey else None,
				'address': pubkey_to_address(pubkey) if len(pubkey) in (33, 65) else None,
			}
			keys.append(entry)

		elif rec_type == 'ckey' and pubkey:
			# ckey value is encrypted private key — cannot decode without passphrase
			# but we record the pubkey and encrypted blob
			compressed = len(pubkey) == 33
			entry = {
				'type': 'ckey',
				'pubkey_hex': pubkey.hex(),
				'encrypted_privkey_hex': v_data.hex(),
				'address': pubkey_to_address(pubkey) if len(pubkey) in (33, 65) else None,
				'note': 'encrypted — passphrase required to recover privkey',
			}
			keys.append(entry)

	return keys

def extract_wallet(path):
	with open(path, 'rb') as f:
		data = f.read()

	print(f'[*] file size: {len(data)} bytes')

	# Try BDB page parsing first
	records = scan_bdb_pages(data)
	print(f'[*] BDB page scan: {len(records)} records')

	keys = process_records(records)

	if not keys:
		print('[*] BDB parse yielded no keys — falling back to brute scan')
		raw = brute_scan(data)
		for rtype, pk, privkey in raw:
			compressed = len(pk) == 33
			keys.append({
				'type': rtype,
				'pubkey_hex': pk.hex(),
				'address': pubkey_to_address(pk) if len(pk) in (33, 65) else None,
				'privkey_hex': None,
				'note': 'brute scan — no value extracted',
			})

	return keys

def main():
	if len(sys.argv) < 2:
		print(f'usage: {sys.argv[0]} wallet.dat [wallet2.dat ...]')
		sys.exit(1)

	for path in sys.argv[1:]:
		print(f'\n=== {path} ===')
		if not os.path.exists(path):
			print(f'  ERROR: file not found')
			continue

		try:
			keys = extract_wallet(path)
		except Exception as e:
			print(f'  ERROR: {e}')
			continue

		print(f'[*] total entries: {len(keys)}')
		print()

		mkeys = [k for k in keys if k['type'] == 'mkey']
		if mkeys:
			print(f'  [!] ENCRYPTED WALLET — {len(mkeys)} master key record(s)')
			for mk in mkeys:
				print(f'      mkey raw: {mk["raw_value_hex"][:64]}...')
			print()

		plain = [k for k in keys if k['type'] in ('key', 'wkey') and k.get('privkey_hex')]
		ckeys = [k for k in keys if k['type'] == 'ckey']
		brute = [k for k in keys if 'raw' in k['type']]

		if plain:
			print(f'  [+] plain private keys: {len(plain)}')
			for k in plain:
				print(f'      address : {k["address"]}')
				print(f'      pubkey  : {k["pubkey_hex"]}')
				print(f'      privkey : {k["privkey_hex"]}')
				print(f'      WIF     : {k["wif"]}')
				print()

		if ckeys:
			print(f'  [~] ckey entries (encrypted privkeys): {len(ckeys)}')
			for k in ckeys:
				print(f'      address      : {k["address"]}')
				print(f'      pubkey       : {k["pubkey_hex"]}')
				print(f'      enc_privkey  : {k["encrypted_privkey_hex"]}')
				print()

		if brute:
			print(f'  [?] brute-scan pubkeys (no value): {len(brute)}')
			for k in brute:
				print(f'      address : {k["address"]}')
				print(f'      pubkey  : {k["pubkey_hex"]}')
				print()

		if not plain and not ckeys and not brute and not mkeys:
			print('  no key records found')

if __name__ == '__main__':
	main()
