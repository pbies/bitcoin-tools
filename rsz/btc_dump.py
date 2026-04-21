#!/usr/bin/env python3
"""
Bitcoin Core blockchain parser
Dumps r,s,z,pubkey CSV from all P2PKH and P2PK transaction inputs.

Output CSV columns (one row per signed input):
  txid, input_index, r, s, z, pubkey, block_height, block_hash

Data sources:
  - blocks/blk*.dat       raw block data (transactions + signatures)
  - blocks/index/         LevelDB block index (height, file, offset)

Does NOT require Bitcoin Core to be running.
Reads block files directly.

Usage:
  python3 btc_dump.py --blocks ~/.bitcoin/blocks --out sigs.csv
  python3 btc_dump.py --blocks ~/.bitcoin/blocks --out sigs.csv --start 0 --end 500000
  python3 btc_dump.py --blocks ~/.bitcoin/blocks --out sigs.csv --file blk00000.dat
  python3 btc_dump.py --demo   # parse a synthetic tx and show output
"""

import os
import sys
import csv
import struct
import hashlib
import argparse
import traceback
from pathlib import Path
from io import BytesIO

# ── crypto primitives (no external deps beyond stdlib for parsing) ────────────
def sha256d(data: bytes) -> bytes:
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def hash256_hex(data: bytes) -> str:
	return sha256d(data)[::-1].hex()

# ── Bitcoin script / DER parsing ──────────────────────────────────────────────
def read_varint(buf: BytesIO) -> int:
	b = buf.read(1)
	if not b:
		raise EOFError("varint: unexpected EOF")
	n = b[0]
	if n < 0xfd:
		return n
	elif n == 0xfd:
		return struct.unpack('<H', buf.read(2))[0]
	elif n == 0xfe:
		return struct.unpack('<I', buf.read(4))[0]
	else:
		return struct.unpack('<Q', buf.read(8))[0]

def read_bytes(buf: BytesIO, n: int) -> bytes:
	data = buf.read(n)
	if len(data) != n:
		raise EOFError(f"expected {n} bytes, got {len(data)}")
	return data

def parse_der_sig(der: bytes):
	"""
	Parse DER-encoded ECDSA signature.
	Returns (r, s) as ints, or (None, None) on failure.
	DER format: 30 <len> 02 <rlen> <r> 02 <slen> <s> [sighash_byte]
	"""
	try:
		if len(der) < 8:
			return None, None
		# Strip trailing sighash byte if present
		sig = der[:-1] if der[-1] in (0x01, 0x02, 0x03, 0x81, 0x82, 0x83) else der
		if sig[0] != 0x30:
			return None, None
		# total length
		total_len = sig[1]
		if total_len + 2 != len(sig):
			# try without stripping
			sig = der
			if sig[0] != 0x30:
				return None, None
			total_len = sig[1]
		pos = 2
		if sig[pos] != 0x02:
			return None, None
		r_len = sig[pos + 1]
		pos += 2
		r_bytes = sig[pos:pos + r_len]
		pos += r_len
		if sig[pos] != 0x02:
			return None, None
		s_len = sig[pos + 1]
		pos += 2
		s_bytes = sig[pos:pos + s_len]
		r = int.from_bytes(r_bytes, 'big')
		s = int.from_bytes(s_bytes, 'big')
		return r, s
	except Exception:
		return None, None

def is_compressed_pubkey(pk: bytes) -> bool:
	return len(pk) == 33 and pk[0] in (0x02, 0x03)

def is_uncompressed_pubkey(pk: bytes) -> bool:
	return len(pk) == 65 and pk[0] == 0x04

def is_pubkey(pk: bytes) -> bool:
	return is_compressed_pubkey(pk) or is_uncompressed_pubkey(pk)

def parse_p2pkh_scriptsig(script: bytes):
	"""
	P2PKH scriptSig: <sig> <pubkey>
	Returns (r, s, sig_bytes, pubkey_hex, sighash_type) or None.
	"""
	try:
		buf = BytesIO(script)
		sig_len = buf.read(1)[0]
		if sig_len == 0 or sig_len > 73:
			return None
		sig_bytes = buf.read(sig_len)
		sighash_type = sig_bytes[-1]
		r, s = parse_der_sig(sig_bytes)
		if r is None:
			return None
		pk_len = buf.read(1)[0]
		if pk_len not in (33, 65):
			return None
		pk = buf.read(pk_len)
		if not is_pubkey(pk):
			return None
		return r, s, sig_bytes, pk.hex(), sighash_type
	except Exception:
		return None

def parse_p2pk_scriptsig(script: bytes):
	"""
	P2PK scriptSig: <sig>   (no pubkey in input — pubkey is in the output script)
	Returns (r, s, sig_bytes, sighash_type) or None.
	"""
	try:
		buf = BytesIO(script)
		sig_len = buf.read(1)[0]
		if sig_len == 0 or sig_len > 73:
			return None
		sig_bytes = buf.read(sig_len)
		sighash_type = sig_bytes[-1]
		r, s = parse_der_sig(sig_bytes)
		if r is None:
			return None
		# no more data expected
		remaining = buf.read()
		if remaining:
			return None
		return r, s, sig_bytes, sighash_type
	except Exception:
		return None

def extract_p2pk_pubkey_from_output_script(script: bytes):
	"""
	P2PK output scriptPubKey: <len> <pubkey> OP_CHECKSIG (0xac)
	"""
	try:
		if len(script) in (35, 67) and script[-1] == 0xac:
			pk_len = script[0]
			pk = script[1:1 + pk_len]
			if is_pubkey(pk):
				return pk.hex()
	except Exception:
		pass
	return None

# ── transaction serialization hash (z = sighash) ─────────────────────────────
def compute_sighash(raw_tx: bytes, input_index: int, subscript: bytes,
	sighash_type: int = 1) -> int:
	"""
	Compute SIGHASH_ALL (type 1) for legacy transactions.
	For other sighash types the formula differs; we handle ALL only here
	since it covers >99% of real transactions.
	Returns z as int.
	"""
	if sighash_type & 0x1f != 0x01:
		# SIGHASH_NONE or SIGHASH_SINGLE — skip for now
		return None
	try:
		tx = BytesIO(raw_tx)
		# version
		version = struct.unpack('<I', tx.read(4))[0]
		# inputs
		n_in = read_varint(tx)
		inputs = []
		for i in range(n_in):
			prev_hash	= tx.read(32)
			prev_idx	= tx.read(4)
			script_len	= read_varint(tx)
			script		= tx.read(script_len)
			seq		= tx.read(4)
			inputs.append((prev_hash, prev_idx, script, seq))
		# outputs
		n_out = read_varint(tx)
		outputs = []
		for _ in range(n_out):
			value		= tx.read(8)
			script_len	= read_varint(tx)
			script		= tx.read(script_len)
			outputs.append((value, script))
		locktime = tx.read(4)

		# Rebuild tx with subscript only at input_index, others empty
		def encode_varint(n):
			if n < 0xfd:	return bytes([n])
			elif n <= 0xffff:	return b'\xfd' + struct.pack('<H', n)
			elif n <= 0xffffffff:	return b'\xfe' + struct.pack('<I', n)
			else:			return b'\xff' + struct.pack('<Q', n)

		buf = b''
		buf += struct.pack('<I', version)
		buf += encode_varint(n_in)
		for i, (ph, pi, sc, seq) in enumerate(inputs):
			buf += ph + pi
			if i == input_index:
				buf += encode_varint(len(subscript)) + subscript
			else:
				buf += b'\x00'	# empty script
			buf += seq
		buf += encode_varint(n_out)
		for value, sc in outputs:
			buf += value + encode_varint(len(sc)) + sc
		buf += locktime
		buf += struct.pack('<I', sighash_type)

		z = int.from_bytes(sha256d(buf), 'big')
		return z
	except Exception:
		return None

# ── raw block file parser ─────────────────────────────────────────────────────
MAINNET_MAGIC	= b'\xf9\xbe\xb4\xd9'
TESTNET_MAGIC	= b'\x0b\x11\x09\x07'
REGTEST_MAGIC	= b'\xfa\xbf\xb5\xda'

def iter_blocks_from_file(blk_path: str, magic: bytes = MAINNET_MAGIC):
	"""
	Yields (raw_block_bytes, file_offset) for each block in a blk*.dat file.
	"""
	with open(blk_path, 'rb') as f:
		while True:
			# Find magic bytes
			hdr = f.read(4)
			if len(hdr) < 4:
				break
			if hdr != magic:
				# Try to re-sync — scan forward byte by byte
				data = hdr
				while True:
					b = f.read(1)
					if not b:
						return
					data = data[1:] + b
					if data == magic:
						break
				hdr = magic
			size_bytes = f.read(4)
			if len(size_bytes) < 4:
				break
			size = struct.unpack('<I', size_bytes)[0]
			if size == 0 or size > 4_000_000:
				continue
			offset = f.tell()
			raw = f.read(size)
			if len(raw) < size:
				break
			yield raw, offset

def parse_block_header(raw: bytes):
	"""Returns (block_hash_hex, height_from_coinbase_or_None, prev_hash_hex)."""
	header	= raw[:80]
	bh	= hash256_hex(header)
	prev	= raw[4:36][::-1].hex()
	return bh, prev

def parse_transactions(raw: bytes):
	"""
	Parse all transactions from a raw block (after 80-byte header).
	Yields (txid_hex, raw_tx_bytes, tx_offset_in_block).
	"""
	buf = BytesIO(raw)
	buf.read(80)	# skip header
	n_tx = read_varint(buf)
	for _ in range(n_tx):
		tx_start = buf.tell()
		tx_bytes  = _read_raw_tx(buf)
		txid = hash256_hex(tx_bytes)
		yield txid, tx_bytes, tx_start

def _read_raw_tx(buf: BytesIO) -> bytes:
	"""Read one full legacy transaction from buf, return its raw bytes."""
	start = buf.tell()
	buf.read(4)	# version
	n_in = read_varint(buf)
	# detect segwit marker
	if n_in == 0:
		# segwit: marker=0x00 flag=0x01 already consumed as n_in=0
		buf.read(1)	# flag
		n_in = read_varint(buf)
		segwit = True
	else:
		segwit = False
	for _ in range(n_in):
		buf.read(32 + 4)	# prev hash + index
		sc_len = read_varint(buf)
		buf.read(sc_len)
		buf.read(4)		# sequence
	n_out = read_varint(buf)
	for _ in range(n_out):
		buf.read(8)		# value
		sc_len = read_varint(buf)
		buf.read(sc_len)
	if segwit:
		for _ in range(n_in):
			n_items = read_varint(buf)
			for _ in range(n_items):
				item_len = read_varint(buf)
				buf.read(item_len)
	buf.read(4)	# locktime
	end = buf.tell()
	buf.seek(start)
	return buf.read(end - start)

def parse_tx_inputs(raw_tx: bytes):
	"""
	Parse inputs from a raw transaction.
	Yields (input_index, prev_txid_hex, prev_vout, scriptsig_bytes, sequence).
	Handles segwit (skips witness data for input extraction).
	"""
	buf = BytesIO(raw_tx)
	buf.read(4)	# version
	n_in = read_varint(buf)
	segwit = False
	if n_in == 0:
		buf.read(1)
		n_in = read_varint(buf)
		segwit = True
	inputs = []
	for i in range(n_in):
		prev_hash	= buf.read(32)[::-1].hex()
		prev_vout	= struct.unpack('<I', buf.read(4))[0]
		sc_len		= read_varint(buf)
		scriptsig	= buf.read(sc_len)
		seq		= struct.unpack('<I', buf.read(4))[0]
		inputs.append((i, prev_hash, prev_vout, scriptsig, seq))
	return inputs

# ── output script cache (needed for P2PK pubkey lookup) ──────────────────────
class OutputCache:
	"""
	In-memory map of (txid, vout) -> scriptPubKey bytes.
	For P2PK inputs we need the previous output's script to get the pubkey.
	Built up as blocks are scanned in order.
	Only stores P2PK outputs to keep memory reasonable.
	"""
	def __init__(self, maxsize=2_000_000):
		self._cache	= {}
		self._maxsize	= maxsize

	def add_tx_outputs(self, txid: str, raw_tx: bytes):
		buf = BytesIO(raw_tx)
		buf.read(4)
		n_in = read_varint(buf)
		segwit = False
		if n_in == 0:
			buf.read(1)
			n_in = read_varint(buf)
			segwit = True
		for _ in range(n_in):
			buf.read(32 + 4)
			sc_len = read_varint(buf)
			buf.read(sc_len)
			buf.read(4)
		n_out = read_varint(buf)
		for vout in range(n_out):
			buf.read(8)
			sc_len = read_varint(buf)
			sc = buf.read(sc_len)
			# only cache P2PK outputs
			if extract_p2pk_pubkey_from_output_script(sc):
				if len(self._cache) < self._maxsize:
					self._cache[(txid, vout)] = sc

	def get(self, txid: str, vout: int):
		return self._cache.get((txid, vout))

# ── LevelDB block index (optional — for height-ordered scanning) ──────────────
def load_block_index_plyvel(index_path: str):
	"""
	Read Bitcoin Core's blocks/index LevelDB.
	Returns dict: block_hash_hex -> {height, file, data_pos}.
	Key prefix 'b' = block index record.
	"""
	try:
		import plyvel
	except ImportError:
		return {}
	index = {}
	try:
		db = plyvel.DB(index_path, create_if_missing=False)
		for k, v in db:
			if k[:1] == b'b' and len(k) == 33:
				bh = k[1:].hex()
				buf = BytesIO(v)
				try:
					# varint fields: version, height, n_tx, status, n_tx2,
					#   file, data_pos, undo_pos
					_version	= read_varint(buf)
					height		= read_varint(buf)
					_n_tx		= read_varint(buf)
					_status		= read_varint(buf)
					_n_tx2		= read_varint(buf)
					blk_file	= read_varint(buf)
					data_pos	= read_varint(buf)
					index[bh] = {
						'height':	height,
						'file':		blk_file,
						'data_pos':	data_pos,
					}
				except Exception:
					pass
		db.close()
	except Exception as e:
		print(f"[!] Could not read block index: {e}", file=sys.stderr)
	return index

# ── main scanner ──────────────────────────────────────────────────────────────
def scan_blk_file(blk_path: str, writer: csv.writer, output_cache: OutputCache,
	magic: bytes, height_map: dict, blk_file_num: int,
	start_height: int, end_height: int, stats: dict):
	"""
	Scan one blk*.dat file, extract all P2PKH and P2PK signatures,
	write rows to CSV writer.
	"""
	for raw_block, offset in iter_blocks_from_file(blk_path, magic):
		try:
			bh, prev_hash = parse_block_header(raw_block)

			# Resolve height
			height = -1
			if bh in height_map:
				height = height_map[bh]['height']

			if height != -1:
				if height < start_height or height > end_height:
					stats['skipped_blocks'] += 1
					continue

			stats['blocks'] += 1

			for txid, raw_tx, _ in parse_transactions(raw_block):
				stats['txs'] += 1
				# First pass: cache outputs for P2PK lookup
				output_cache.add_tx_outputs(txid, raw_tx)

				inputs = parse_tx_inputs(raw_tx)
				for (inp_idx, prev_txid, prev_vout, scriptsig, seq) in inputs:
					if not scriptsig:
						continue	# coinbase or segwit native

					pubkey_hex	= None
					r		= None
					s		= None
					sighash_type	= None

					# Try P2PKH first
					p2pkh = parse_p2pkh_scriptsig(scriptsig)
					if p2pkh:
						r, s, sig_bytes, pubkey_hex, sighash_type = p2pkh
					else:
						# Try P2PK
						p2pk = parse_p2pk_scriptsig(scriptsig)
						if p2pk:
							r, s, sig_bytes, sighash_type = p2pk
							# Look up pubkey from previous output
							prev_sc = output_cache.get(prev_txid, prev_vout)
							if prev_sc:
								pubkey_hex = extract_p2pk_pubkey_from_output_script(prev_sc)

					if r is None or s is None:
						continue

					# Compute z (sighash)
					# subscript = previous output's scriptPubKey
					# For P2PKH the subscript is the standard OP_DUP OP_HASH160 ... script
					# We don't have it cached (would need full UTXO set),
					# so we compute it from the scriptsig pubkey:
					if pubkey_hex:
						pk_bytes = bytes.fromhex(pubkey_hex)
						pk_hash = hashlib.new('ripemd160',
							hashlib.sha256(pk_bytes).digest()).digest()
						subscript = (
							b'\x76\xa9\x14' + pk_hash + b'\x88\xac'
						)
					else:
						# P2PK: subscript from previous output script
						prev_sc = output_cache.get(prev_txid, prev_vout)
						subscript = prev_sc if prev_sc else b''

					z = compute_sighash(raw_tx, inp_idx, subscript,
						sighash_type if sighash_type else 1)

					if z is None:
						stats['sighash_fail'] += 1
						continue

					stats['sigs'] += 1
					writer.writerow([
						txid,
						inp_idx,
						hex(r),
						hex(s),
						hex(z),
						pubkey_hex or '',
						height,
						bh,
					])

		except Exception:
			stats['errors'] += 1
			if stats['errors'] <= 10:
				traceback.print_exc(file=sys.stderr)

# ── demo mode ─────────────────────────────────────────────────────────────────
def demo():
	"""
	Build a synthetic P2PKH transaction, parse it, verify r/s/z extraction.
	No Bitcoin Core installation required.
	"""
	import hashlib, random

	# Minimal constants
	N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
	P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
	Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
	Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
	G = (Gx, Gy)

	def modinv(a, m): return pow(a, -1, m)
	def point_add(P1, P2):
		if P1 is None: return P2
		if P2 is None: return P1
		x1,y1=P1; x2,y2=P2
		if x1==x2:
			if y1!=y2: return None
			lam=(3*x1*x1*modinv(2*y1,P))%P
		else:
			lam=((y2-y1)*modinv(x2-x1,P))%P
		x3=(lam*lam-x1-x2)%P
		y3=(lam*(x1-x3)-y1)%P
		return x3,y3
	def point_mul(k, pt):
		res=None; add=pt
		while k:
			if k&1: res=point_add(res,add)
			add=point_add(add,add); k>>=1
		return res

	def encode_varint(n):
		if n<0xfd: return bytes([n])
		elif n<=0xffff: return b'\xfd'+struct.pack('<H',n)
		elif n<=0xffffffff: return b'\xfe'+struct.pack('<I',n)
		else: return b'\xff'+struct.pack('<Q',n)

	def encode_der(r, s):
		def enc_int(v):
			b = v.to_bytes((v.bit_length()+7)//8,'big')
			if b[0]&0x80: b=b'\x00'+b
			return b
		rb=enc_int(r); sb=enc_int(s)
		body=b'\x02'+bytes([len(rb)])+rb+b'\x02'+bytes([len(sb)])+sb
		return b'\x30'+bytes([len(body)])+body+b'\x01'  # SIGHASH_ALL

	# Generate key pair
	d = random.randrange(1, N)
	pub_pt = point_mul(d, G)
	pub_bytes = (b'\x02' if pub_pt[1]%2==0 else b'\x03') + pub_pt[0].to_bytes(32,'big')

	# P2PKH subscript
	pk_hash = hashlib.new('ripemd160', hashlib.sha256(pub_bytes).digest()).digest()
	subscript = b'\x76\xa9\x14' + pk_hash + b'\x88\xac'

	# Build a minimal tx skeleton (1 input, 1 output) to get the sighash
	prev_txid	= bytes(32)
	prev_vout	= struct.pack('<I', 0)
	sequence	= b'\xff\xff\xff\xff'
	value		= struct.pack('<Q', 50_000_000)
	out_script	= subscript
	version		= struct.pack('<I', 1)
	locktime	= struct.pack('<I', 0)
	sighash_flag	= struct.pack('<I', 1)

	# Sighash preimage
	preimage = (version
		+ encode_varint(1)
		+ prev_txid + prev_vout
		+ encode_varint(len(subscript)) + subscript
		+ sequence
		+ encode_varint(1)
		+ value + encode_varint(len(out_script)) + out_script
		+ locktime + sighash_flag)
	z = int.from_bytes(sha256d(preimage), 'big')

	# Sign
	k = random.randrange(1, N)
	R_pt = point_mul(k, G)
	r = R_pt[0] % N
	s = (modinv(k, N) * (z + r * d)) % N

	der_sig = encode_der(r, s)

	# Build real scriptSig
	scriptsig = (bytes([len(der_sig)]) + der_sig
		+ bytes([len(pub_bytes)]) + pub_bytes)

	# Build full raw tx with the real scriptsig
	raw_tx = (version
		+ encode_varint(1)
		+ prev_txid + prev_vout
		+ encode_varint(len(scriptsig)) + scriptsig
		+ sequence
		+ encode_varint(1)
		+ value + encode_varint(len(out_script)) + out_script
		+ locktime)

	txid = hash256_hex(raw_tx)

	# Now parse it back
	parsed = parse_p2pkh_scriptsig(scriptsig)
	r2, s2, _, pk2, _ = parsed
	inp_idx = 0
	z2 = compute_sighash(raw_tx, inp_idx, subscript, 1)

	print("=== DEMO: synthetic P2PKH transaction ===")
	print(f"txid        : {txid}")
	print(f"private key : {hex(d)}")
	print(f"pubkey      : {pub_bytes.hex()}")
	print(f"r (signed)  : {hex(r)}")
	print(f"r (parsed)  : {hex(r2)}")
	print(f"r match     : {r == r2}")
	print(f"s (signed)  : {hex(s)}")
	print(f"s (parsed)  : {hex(s2)}")
	print(f"s match     : {s == s2}")
	print(f"z (signed)  : {hex(z)}")
	print(f"z (parsed)  : {hex(z2)}")
	print(f"z match     : {z == z2}")
	print()
	print("CSV row that would be written:")
	print("txid,input_index,r,s,z,pubkey,block_height,block_hash")
	print(f"{txid},0,{hex(r2)},{hex(s2)},{hex(z2)},{pk2},-1,<block_hash>")

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
	ap = argparse.ArgumentParser(
		description="Bitcoin Core block file parser — dumps r,s,z,pubkey CSV",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Demo mode (no Bitcoin Core needed):
  python3 btc_dump.py --demo

  # Scan all block files:
  python3 btc_dump.py --blocks ~/.bitcoin/blocks --out sigs.csv

  # Scan blocks 0-200000 only:
  python3 btc_dump.py --blocks ~/.bitcoin/blocks --out sigs.csv --start 0 --end 200000

  # Scan a single blk file:
  python3 btc_dump.py --blocks ~/.bitcoin/blocks --out sigs.csv --file blk00000.dat

  # Testnet:
  python3 btc_dump.py --blocks ~/.bitcoin/testnet3/blocks --out sigs.csv --testnet

Output CSV columns:
  txid, input_index, r, s, z, pubkey, block_height, block_hash

Feed output directly to ecdsa_analysis.py:
  python3 ecdsa_analysis.py --nonce-reuse sigs.csv
  python3 ecdsa_analysis.py --known-k sigs.csv --nonces nonces.txt
		"""
	)
	ap.add_argument('--demo',	action='store_true',
		help='Parse a synthetic transaction (no Bitcoin Core needed)')
	ap.add_argument('--blocks',	metavar='DIR',
		help='Path to Bitcoin Core blocks/ directory')
	ap.add_argument('--out',	metavar='CSV',
		default='sigs.csv',
		help='Output CSV file (default: sigs.csv)')
	ap.add_argument('--start',	metavar='N', type=int, default=0,
		help='Start block height (default: 0)')
	ap.add_argument('--end',	metavar='N', type=int, default=10_000_000,
		help='End block height (default: all)')
	ap.add_argument('--file',	metavar='FILENAME',
		help='Scan only this blk*.dat filename (e.g. blk00000.dat)')
	ap.add_argument('--testnet',	action='store_true',
		help='Use testnet magic bytes')
	ap.add_argument('--regtest',	action='store_true',
		help='Use regtest magic bytes')
	ap.add_argument('--no-index',	action='store_true',
		help='Skip LevelDB block index (no height filtering, faster startup)')
	args = ap.parse_args()

	if args.demo:
		demo()
		return

	if not args.blocks:
		ap.print_help()
		sys.exit(1)

	blocks_dir = Path(args.blocks)
	if not blocks_dir.exists():
		print(f"[!] Blocks directory not found: {blocks_dir}")
		sys.exit(1)

	magic = MAINNET_MAGIC
	if args.testnet:	magic = TESTNET_MAGIC
	if args.regtest:	magic = REGTEST_MAGIC

	# Load block index for height mapping
	height_map = {}
	if not args.no_index:
		index_path = str(blocks_dir / 'index')
		if Path(index_path).exists():
			print(f"[*] Loading block index from {index_path}...")
			height_map = load_block_index_plyvel(index_path)
			print(f"[+] Loaded {len(height_map)} block index entries")
		else:
			print(f"[!] Block index not found at {index_path}, scanning without height filtering")

	# Collect blk files to scan
	if args.file:
		blk_files = [blocks_dir / args.file]
	else:
		blk_files = sorted(blocks_dir.glob('blk*.dat'))

	if not blk_files:
		print(f"[!] No blk*.dat files found in {blocks_dir}")
		sys.exit(1)

	print(f"[*] Scanning {len(blk_files)} block file(s)")
	print(f"[*] Height range: {args.start} – {args.end}")
	print(f"[*] Output: {args.out}\n")

	output_cache = OutputCache()
	stats = {
		'blocks': 0, 'txs': 0, 'sigs': 0,
		'skipped_blocks': 0, 'sighash_fail': 0, 'errors': 0,
	}

	with open(args.out, 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['txid', 'input_index', 'r', 's', 'z',
			'pubkey', 'block_height', 'block_hash'])

		for blk_path in blk_files:
			blk_num = int(str(blk_path.stem).replace('blk', ''))
			print(f"  [{blk_path.name}]  ", end='', flush=True)
			before = stats['sigs']
			scan_blk_file(
				str(blk_path), writer, output_cache, magic,
				height_map, blk_num,
				args.start, args.end, stats
			)
			print(f"+{stats['sigs'] - before} sigs  "
				f"(total: {stats['sigs']}  blocks: {stats['blocks']}  "
				f"txs: {stats['txs']}  errors: {stats['errors']})")

	print(f"\n[+] Done.")
	print(f"    Blocks scanned : {stats['blocks']}")
	print(f"    Transactions   : {stats['txs']}")
	print(f"    Signatures out : {stats['sigs']}")
	print(f"    Sighash fails  : {stats['sighash_fail']}")
	print(f"    Parse errors   : {stats['errors']}")
	print(f"    Output         : {args.out}")

if __name__ == '__main__':
	main()
