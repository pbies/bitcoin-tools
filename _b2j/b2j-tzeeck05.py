#!/usr/bin/env python3

# This software is
# Copyright (c) 2012-2018 Dhiru Kholia <dhiru at openwall.com>
# Copyright (c) 2019 Solar Designer
# Copyright (c) 2019 exploide
# Redistribution and use in source and binary forms, with or without
# modification, are permitted.  (This is a heavily cut-down "BSD license".)

import binascii
import glob
import logging
import os
import struct
import sys

try:
	from bsddb3.db import *
	from bsddb3.db import DBPageNotFoundError, DBError
except ImportError:
	try:
		from bsddb.db import *
		from bsddb.db import DBPageNotFoundError, DBError
	except ImportError:
		sys.stderr.write("Error: bsddb3 is not installed\n")
		sys.exit(1)


def hexstr(bytestr):
	return binascii.hexlify(bytestr).decode('ascii')


class SerializationError(Exception):
	pass


class BCDataStream:
	def __init__(self):
		self.input = None
		self.read_cursor = 0

	def clear(self):
		self.input = None
		self.read_cursor = 0

	def write(self, data):
		if self.input is None:
			self.input = data
		else:
			self.input += data

	def read_string(self):
		if self.input is None:
			raise SerializationError("call write(bytes) before trying to deserialize")
		try:
			length = self.read_compact_size()
		except IndexError:
			raise SerializationError("attempt to read past end of buffer")
		return self.read_bytes(length).decode('ascii')

	def read_bytes(self, length):
		try:
			result = self.input[self.read_cursor:self.read_cursor + length]
			self.read_cursor += length
			return result
		except IndexError:
			raise SerializationError("attempt to read past end of buffer")

	def read_uint32(self):
		return self._read_num('<I')

	def read_compact_size(self):
		size = self.input[self.read_cursor]
		if isinstance(size, str):
			size = ord(size)
		self.read_cursor += 1
		if size == 253:
			size = self._read_num('<H')
		elif size == 254:
			size = self._read_num('<I')
		elif size == 255:
			size = self._read_num('<Q')
		return size

	def _read_num(self, fmt):
		(i,) = struct.unpack_from(fmt, self.input, self.read_cursor)
		self.read_cursor += struct.calcsize(fmt)
		return i


# BDB btree leaf page layout constants
BDB_BTREE_LEAF	= 5		# page type byte at offset 25
BDB_HDR_SIZE	= 26	# fixed page header length
BITEM_HDR		= 3		# item header: 2-byte length + 1-byte type


def _parse_mkey_value(vbuf):
	"""Parse mkey value bytes -> dict or None."""
	vds = BCDataStream()
	vds.write(vbuf)
	try:
		enc_key = vds.read_bytes(vds.read_compact_size())
		salt    = vds.read_bytes(vds.read_compact_size())
		method  = vds.read_uint32()
		iters   = vds.read_uint32()
		return {
			'encrypted_key':         hexstr(enc_key),
			'salt':                  hexstr(salt),
			'nDerivationMethod':     method,
			'nDerivationIterations': iters,
		}
	except Exception:
		return None


def _scan_pages(data, pagesize, mkey_tag):
	"""Walk BDB btree leaf pages of given size, return parsed mkey or None."""
	num_pages = len(data) // pagesize
	for pno in range(num_pages):
		page = data[pno * pagesize:(pno + 1) * pagesize]
		if len(page) < BDB_HDR_SIZE:
			continue
		page_type = page[25]
		if page_type != BDB_BTREE_LEAF:
			continue
		num_entries = struct.unpack_from('<H', page, 20)[0]
		for i in range(num_entries):
			idx_off = BDB_HDR_SIZE + i * 2
			if idx_off + 2 > pagesize:
				break
			item_off = struct.unpack_from('<H', page, idx_off)[0]
			if item_off + BITEM_HDR > pagesize:
				continue
			item_len  = struct.unpack_from('<H', page, item_off)[0]
			item_type = page[item_off + 2]
			if item_type != 1:
				continue
			item_data = page[item_off + BITEM_HDR:item_off + BITEM_HDR + item_len]
			if item_data != mkey_tag:
				continue
			# value is the next entry
			next_idx_off = BDB_HDR_SIZE + (i + 1) * 2
			if next_idx_off + 2 > pagesize:
				continue
			val_off = struct.unpack_from('<H', page, next_idx_off)[0]
			if val_off + BITEM_HDR > pagesize:
				continue
			val_len  = struct.unpack_from('<H', page, val_off)[0]
			val_data = page[val_off + BITEM_HDR:val_off + BITEM_HDR + val_len]
			result = _parse_mkey_value(val_data)
			if result:
				return result
	return None


def _naive_scan(data, mkey_tag):
	"""No page structure: find mkey_tag anywhere, try to parse value after it."""
	pos = 0
	while True:
		idx = data.find(mkey_tag, pos)
		if idx == -1:
			break
		for offset in range(0, 32):
			vstart = idx + len(mkey_tag) + offset
			vbuf   = data[vstart:vstart + 200]
			result = _parse_mkey_value(vbuf)
			if result and 8 <= len(result['salt']) <= 72:
				return result
		pos = idx + 1
	return None


def _raw_scan_mkey(walletfile):
	"""Raw byte fallback for DBPageNotFoundError / any bsddb3 failure."""
	MKEY_TAG = b'\x04mkey'
	try:
		with open(walletfile, 'rb') as f:
			data = f.read()
	except IOError as e:
		sys.stderr.write("%s: cannot read file: %s\n" % (walletfile, e))
		return None

	for pagesize in (4096, 8192, 1024, 2048, 16384, 32768, 65536, 512):
		mkey = _scan_pages(data, pagesize, MKEY_TAG)
		if mkey:
			sys.stderr.write("%s: raw scan recovered mkey (pagesize=%d)\n" % (walletfile, pagesize))
			return mkey

	mkey = _naive_scan(data, MKEY_TAG)
	if mkey:
		sys.stderr.write("%s: naive byte scan recovered mkey\n" % walletfile)
	return mkey


def open_wallet(walletfile):
	db = DB()
	flags = DB_THREAD | DB_RDONLY
	try:
		r = db.open(walletfile, "main", DB_BTREE, flags)
	except DBError as e:
		logging.error(e)
		r = True
	if r is not None:
		sys.stderr.write("%s: bsddb3 open failed\n" % walletfile)
		return None
	return db


def parse_wallet(db, item_callback):
	kds = BCDataStream()
	vds = BCDataStream()
	for (key, value) in db.items():
		d = {}
		kds.clear(); kds.write(key)
		vds.clear(); vds.write(value)
		try:
			record_type = kds.read_string()
		except Exception:
			continue
		d["__key__"] = key
		d["__value__"] = value
		d["__type__"] = record_type
		try:
			if record_type == "mkey":
				d['encrypted_key'] = vds.read_bytes(vds.read_compact_size())
				d['salt']          = vds.read_bytes(vds.read_compact_size())
				d['nDerivationMethod']     = vds.read_uint32()
				d['nDerivationIterations'] = vds.read_uint32()
			item_callback(record_type, d)
		except Exception:
			sys.stderr.write("ERROR parsing record type '%s'\n" % record_type)
			sys.stderr.write("key hex: %s\n" % hexstr(key))
			sys.stderr.write("value hex: %s\n" % hexstr(value))


def read_wallet_bsddb(walletfile):
	db = open_wallet(walletfile)
	if db is None:
		return None

	mkey = {}

	def item_callback(record_type, d):
		if record_type == "mkey":
			mkey['encrypted_key']         = hexstr(d['encrypted_key'])
			mkey['salt']                  = hexstr(d['salt'])
			mkey['nDerivationMethod']     = d['nDerivationMethod']
			mkey['nDerivationIterations'] = d['nDerivationIterations']

	try:
		parse_wallet(db, item_callback)
	except (DBPageNotFoundError, DBError) as e:
		sys.stderr.write("%s: bsddb3 iteration error: %s\n" % (walletfile, e))
		db.close()
		return None

	db.close()
	return mkey if 'salt' in mkey else None


def read_wallet(walletfile):
	mkey = read_wallet_bsddb(walletfile)
	if mkey is not None:
		return mkey
	sys.stderr.write("%s: bsddb3 path failed, falling back to raw scan\n" % walletfile)
	return _raw_scan_mkey(walletfile)


def process_wallet(walletfile, outfile):
	mkey = read_wallet(walletfile)
	if mkey is None:
		sys.stderr.write("%s: no mkey found (not encrypted or unreadable)\n" % walletfile)
		return

	cry_method = mkey['nDerivationMethod']
	if cry_method != 0:
		sys.stderr.write("%s: unknown derivation method %d\n" % (walletfile, cry_method))
		return

	cry_salt   = mkey['salt']
	salt_len   = len(cry_salt)

	if salt_len == 16:
		expected_mkey_len = 96
	elif salt_len == 36:
		expected_mkey_len = 160
	else:
		sys.stderr.write("%s: unsupported salt size %d\n" % (walletfile, salt_len))
		return

	if len(mkey['encrypted_key']) != expected_mkey_len:
		sys.stderr.write("%s: unsupported master key size %d\n" % (walletfile, len(mkey['encrypted_key'])))
		return

	cry_master = mkey['encrypted_key'][-64:]
	cry_rounds = mkey['nDerivationIterations']

	line = "$bitcoin$%s$%s$%s$%s$%s$2$00$2$00\n" % (
		len(cry_master), cry_master, len(cry_salt), cry_salt, cry_rounds
	)

	sys.stdout.write(line)
	outfile.write(line)
	outfile.flush()
	return cry_master


if __name__ == '__main__':
	# Single-file mode: called by the bash wrapper with a path argument
	if len(sys.argv) == 2:
		with open(os.devnull, 'w') as devnull:
			process_wallet(sys.argv[1], devnull)
		sys.exit(0)

	dat_files = sorted(glob.glob("*.dat"))
	if not dat_files:
		sys.stderr.write("No .dat files found in current directory\n")
		sys.exit(1)

	used_names = set()

	with open("hashes.txt", "a") as outfile:
		for walletfile in dat_files:
			sys.stderr.write("Processing: %s\n" % walletfile)
			cry_master = process_wallet(walletfile, outfile)
			if cry_master is None:
				continue

			candidate = cry_master + ".dat"
			n = 2
			while candidate in used_names or (os.path.exists(candidate) and candidate != walletfile):
				candidate = "%s (%02d).dat" % (cry_master, n)
				n += 1

			used_names.add(candidate)
			if candidate != walletfile:
				try:
					os.rename(walletfile, candidate)
					sys.stderr.write("%s -> %s\n" % (walletfile, candidate))
				except OSError as e:
					sys.stderr.write("Cannot rename %s: %s\n" % (walletfile, e))
			else:
				sys.stderr.write("%s: already named correctly\n" % walletfile)

	print('\a', end='', file=sys.stderr)
