#!/usr/bin/env python3

import base58 as b58
import hashlib as hl
import random as rnd
from itertools import product as prod

def hex_b58(b58_str):
	try:
		dec = b58.b58decode(b58_str)
		hex_str = dec.hex()[2:-10]
		return hex_str
	except Exception:
		return None

def rand_cb58(txt):
	invalid = {'0', 'O', 'I', 'l'}
	res = ''
	for c in txt:
		up, lo = c.upper(), c.lower()
		opts = {up, lo} - invalid
		res += c if c in invalid else rnd.choice(list(opts)) if opts else c
	return res

def crack_addr(fix_hex, goal, prefix):
	if len(fix_hex) % 2:
		fix_hex += '0'

	fix_bytes = bytes.fromhex(fix_hex)
	fix_len = len(fix_bytes)
	pad = 20 - fix_len

	if fix_len > 20 or pad < 0:
		return False

	def gen_addr(rbytes):
		rmd = fix_bytes + rbytes
		payload = b'\x00' + rmd
		chk = hl.sha256(hl.sha256(payload).digest()).digest()[:4]
		addr = b58.b58encode(payload + chk).decode()
		return addr, rmd

	if pad <= 2:
		for c in prod(range(256), repeat=pad):
			rb = bytes(c)
			addr, rmd = gen_addr(rb)
			if addr.lower().startswith(prefix.lower()):
				print(f"[prefix match] {addr} — RMD160: {rmd.hex()}")
				return "prefix"
			if addr.lower() == goal.lower():
				print(f"[TARGET FOUND] {addr} — RMD160: {rmd.hex()}")
				return "goal"
	else:
		while True:
			rb = bytes(rnd.getrandbits(8) for _ in range(pad))
			addr, rmd = gen_addr(rb)
			if addr.lower().startswith(prefix.lower()):
				print(f"[prefix match] {addr} — RMD160: {rmd.hex()}")
				return "prefix"
			if addr.lower() == goal.lower():
				print(f"[TARGET FOUND] {addr} — RMD160: {rmd.hex()}")
				return "goal"

if __name__ == "__main__":
	goal = "1bitcointaLkforumburnLegacyaddress"
	prefix = "1BitcoinTALKforumBurnLegacyaddr"

	while True:
		tgt = rand_cb58(goal)
		tgt_hex = hex_b58(tgt)

		if not tgt_hex:
			continue
		if len(bytes.fromhex(tgt_hex)) >= 20:
			continue

		result = crack_addr(tgt_hex, tgt, prefix)
		if result in {"prefix", "goal"}:
			break
