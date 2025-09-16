#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip3 install plyvel python-bitcoinlib

# does not work with ~/.bitcoin/chainstate in WSL2!

import argparse, os, csv, struct, binascii
import plyvel
from io import BytesIO
from bitcoin.core import x as b2lx
from bitcoin.core import CScript
from bitcoin.wallet import CBitcoinAddress, P2PKHBitcoinAddress, P2SHBitcoinAddress
# from bitcoin.core.key import CKey
# from bitcoin import SelectParams

# --- helpers ---------------------------------------------------------------

def read_varint(f):
	# Bitcoin Core's CompactSize
	c = f.read(1)
	if not c:
		raise EOFError
	n = c[0]
	if n < 253:
		return n
	if n == 253:
		return struct.unpack("<H", f.read(2))[0]
	if n == 254:
		return struct.unpack("<I", f.read(4))[0]
	return struct.unpack("<Q", f.read(8))[0]

def read_compact_size(data, pos):
	# for parsing within buffers (returns value, new_pos)
	first = data[pos]
	pos += 1
	if first < 253:
		return first, pos
	if first == 253:
		val = struct.unpack_from("<H", data, pos)[0]
		return val, pos + 2
	if first == 254:
		val = struct.unpack_from("<I", data, pos)[0]
		return val, pos + 4
	val = struct.unpack_from("<Q", data, pos)[0]
	return val, pos + 8

def decompress_amount(x):
	# Port z Core: DecompressAmount (amount compression)
	if x == 0:
		return 0
	x -= 1
	e = x % 10
	x //= 10
	n = 0
	if e < 9:
		d = (x % 9) + 1
		x //= 9
		n = x * 10 + d
	else:
		n = x + 1
	for _ in range(e):
		n *= 10
	return n

def decode_outpoint(key_bytes):
	# key format: [0x43 'C'] + txid(32 LE) + varint(vout)
	assert key_bytes[0] == 0x43
	txid_le = key_bytes[1:33]
	txid = binascii.hexlify(txid_le[::-1]).decode()
	# the rest is varint of vout
	vout, _pos = read_compact_size(key_bytes, 33)
	return txid, vout

def decompress_script(f):
	# Script compression used in chainstate (Core's CTxOutCompressor)
	# Types:
	# 0: raw script (length = varint, then bytes)
	# 1: P2PKH (20b hash follows)
	# 2: P2SH  (20b hash follows)
	# 3..5: compressed pubkeys -> P2PK; rzadkie dziś – zwrócimy raw klucz jako scriptPubKey
	code = read_varint(f)
	if code == 0:
		size = read_varint(f)
		return f.read(size)
	if code == 1:
		h160 = f.read(20)
		# DUP HASH160 <20> <h160> EQUALVERIFY CHECKSIG
		return b"\x76\xa9\x14" + h160 + b"\x88\xac"
	if code == 2:
		h160 = f.read(20)
		# HASH160 <20> <h160> EQUAL
		return b"\xa9\x14" + h160 + b"\x87"
	# 3..5: compressed pubkey to P2PK
	if code in (3,4,5):
		# Recreate 33-byte compressed pubkey from 32b X + yparity embedded in code
		y_parity = (code - 2)  # 1=>0x02, 2=>0x03, 3=>0x04? (w praktyce 3=>0x02,4=>0x03,5=>0x04 dla uncompressed); zachowawczo:
		x = f.read(32)
		if code in (3,4):
			pub = bytes([0x02 + (code - 3)]) + x
		else:
			# uncompressed 65B (rzadkie); bezpiecznie zbuduj 65B: 0x04 + X + Y?? – nie mamy Y; więc oddaj „minimalny” P2PK z 33B
			pub = b"\x02" + x
		# script: <33> <pubkey> CHECKSIG
		return b"\x21" + pub + b"\xac"
	# Fallback
	size = read_varint(f)
	return f.read(size)

def parse_coin(value_bytes):
	# value format (Coin): varint(code) where:
	# code = (height << 1) | coinbase_flag
	# then amount (compressed varint), then script (compressed)
	f = BytesIO(value_bytes)
	code = read_varint(f)
	height = code >> 1
	coinbase = (code & 1) == 1
	amount_comp = read_varint(f)
	amount = decompress_amount(amount_comp)
	script = decompress_script(f)
	return height, coinbase, amount, script

def deobfuscate(value, xor_key):
	if not xor_key:
		return value
	# Core stores obfuscation key prefixed with its length (1 byte) in 'obfuscate_key'
	# In values: bytes are XORed with key repeated
	out = bytearray(len(value))
	for i, b in enumerate(value):
		out[i] = b ^ xor_key[i % len(xor_key)]
	return bytes(out)

def script_to_address(script, network='mainnet'):
	# Best-effort: P2PKH / P2SH / P2WPKH / P2WSH; reszta: ""
	try:
		cs = CScript(script)
		# prosta próba: python-bitcoinlib sam rozpozna standardowe formy przy konwersji do address?
		# Nie ma bezpośredniej, więc ręcznie dla typów:
		# P2PKH
		if len(script) == 25 and script[:3] == b"\x76\xa9\x14" and script[-2:] == b"\x88\xac":
			return str(P2PKHBitcoinAddress.from_scriptPubKey(cs))
		# P2SH
		if len(script) == 23 and script[:2] == b"\xa9\x14" and script[-1:] == b"\x87":
			return str(P2SHBitcoinAddress.from_scriptPubKey(cs))
		# P2WPKH: 0 <20>
		if len(script) == 22 and script[0] == 0x00 and script[1] == 0x14:
			# bech32 adresy: python-bitcoinlib ma FromScriptPubKey?
			from bitcoin.wallet import CBitcoinAddressError
			try:
				return CBitcoinAddress.from_scriptPubKey(cs).__str__()
			except Exception:
				return ""
		# P2WSH: 0 <32>
		if len(script) == 34 and script[0] == 0x00 and script[1] == 0x20:
			try:
				return CBitcoinAddress.from_scriptPubKey(cs).__str__()
			except Exception:
				return ""
		return ""
	except Exception:
		return ""

# --- main ------------------------------------------------------------------

def main():
	parser = argparse.ArgumentParser(description="Dump UTXO set from Bitcoin Core chainstate (Python port of utxodump).")
	parser.add_argument("--chainstate", required=True, help="Ścieżka do katalogu chainstate (np. ~/.bitcoin/chainstate)")
	parser.add_argument("--out", default="utxos.csv", help="Plik wyjściowy CSV")
	parser.add_argument("--limit", type=int, default=0, help="Opcjonalny limit liczby rekordów (0 = wszystko)")
	args = parser.parse_args()

	db = plyvel.DB(args.chainstate, create_if_missing=False)
	try:
		# Pobierz klucz obfuskacji
		ob_key = b""
		rec = db.get(b'obfuscate_key')
		if rec:
			# format: 1 bajt długości + klucz
			if len(rec) > 0:
				l = rec[0]
				ob_key = rec[1:1+l]
		# CSV header
		with open(args.out, "w", newline="") as f:
			w = csv.writer(f)
			w.writerow(["txid","vout","height","coinbase","amount_sats","scriptpubkey_hex","address"])
			count = 0
			for key, val in db:
				# klucze UTXO zaczynają się od 0x43 ('C')
				if not key or key[0] != 0x43:
					continue
				try:
					txid, vout = decode_outpoint(key)
					val_deob = deobfuscate(val, ob_key)
					height, coinbase, amount, script = parse_coin(val_deob)
					addr = script_to_address(script, 'mainnet')
					w.writerow([txid, vout, height, 1 if coinbase else 0, amount, binascii.hexlify(script).decode(), addr])
					count += 1
					if args.limit and count >= args.limit:
						break
				except Exception:
					# pomiń trudne/egzotyczne wpisy, ale nie przerywaj zrzutu
					continue
		print(f"OK: zapisano do {args.out}")
	finally:
		db.close()

if __name__ == "__main__":
	main()
