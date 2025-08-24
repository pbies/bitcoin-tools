#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import requests

# --- Config ---
# Provide your Alchemy API key via env var ALCHEMY_API_KEY or hardcode below.
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "").strip()
if not ALCHEMY_API_KEY:
	# Fallback to a placeholder (replace with your real key or set env var)
	ALCHEMY_API_KEY = ""
ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
ERROR_FILE  = "errors.txt"
MAX_WORKERS = 4  # as requested
TIMEOUT = 30

# Input format (per line):
# 0xEthAddress[,0xTokenAddress1,0xTokenAddress2,...]
#
# This version always fetches *all* token balances for the ETH address first
# (i.e., without filtering by the optional token list). If token addresses are
# present on the line, they will be ensured to appear in output even if zero.
#
# Output format per address:
# <ethAddress>
# 	ETH:<wei>:<ether>
# 	<tokenContract>:<raw_wei>:<human_balance>:<symbol>(decimals d)
#
# Results are written incrementally to OUTPUT_FILE; errors go to ERROR_FILE.

session = requests.Session()
session.headers.update({"accept": "application/json", "content-type": "application/json"})
write_lock = threading.Lock()
meta_lock = threading.Lock()

# Cache for token metadata to avoid repeated calls
token_meta_cache = {}

def alchemy_post(method, params):
	"""Call Alchemy JSON-RPC with basic retries."""
	payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
	for attempt in range(3):
		try:
			resp = session.post(ALCHEMY_URL, json=payload, timeout=TIMEOUT)
			resp.raise_for_status()
			return resp.json()
		except Exception:
			if attempt == 2:
				raise
			time.sleep(1.5 * (attempt + 1))
	return None

def get_eth_balance(addr):
	"""Return (wei_int, ether_float_str)."""
	res = alchemy_post("eth_getBalance", [addr, "latest"])
	if not res or "result" not in res:
		raise RuntimeError(f"eth_getBalance failed for {addr}")
	wei = int(res["result"], 16)
	ether = wei / 10**18
	ether_str = f"{ether:.18f}".rstrip("0").rstrip(".") if ether != 0 else "0"
	return wei, ether_str

def get_token_metadata(contract_addr):
	"""Fetch and cache token decimals + symbol via alchemy_getTokenMetadata."""
	k = contract_addr.lower()
	with meta_lock:
		if k in token_meta_cache:
			return token_meta_cache[k]
	try:
		res = alchemy_post("alchemy_getTokenMetadata", [{"contractAddress": contract_addr}])
		if not res or "result" not in res:
			raise RuntimeError("no result")
		r = res["result"]
		decimals = r.get("decimals")
		symbol = r.get("symbol") or ""
		if decimals is None:
			decimals = 18
		info = (int(decimals), str(symbol))
		with meta_lock:
			token_meta_cache[k] = info
		return info
	except Exception:
		info = (18, "")
		with meta_lock:
			token_meta_cache[k] = info
		return info

def get_all_token_balances(addr):
	"""Use alchemy_getTokenBalances with no filter to get all balances for the address."""
	res = alchemy_post("alchemy_getTokenBalances", [addr])
	if not res or "result" not in res or "tokenBalances" not in res["result"]:
		raise RuntimeError(f"alchemy_getTokenBalances failed for {addr}")
	return res["result"]["tokenBalances"]

def parse_line(line):
	parts = [p.strip() for p in line.strip().split(",") if p.strip()]
	print(parts)
	if not parts:
		return None, []
	addr = parts[0]
	tokens = list(dict.fromkeys([p for p in parts[1:] if p]))  # dedupe, keep order
	return addr, tokens

def is_eth_address(s):
	return isinstance(s, str) and s.startswith("0x") and len(s) == 42

def process_one(line):
	addr, tokens_hint = parse_line(line)
	if not addr or not is_eth_address(addr):
		raise ValueError(f"Invalid ETH address in line: {line.strip()}")
	for t in tokens_hint:
		if not is_eth_address(t):
			raise ValueError(f"Invalid token address '{t}' for {addr}")

	# 1) Token balances FIRST (unfiltered) to minimize extra round-trips later.
	all_tok_bal = get_all_token_balances(addr)
	# Build mapping contract->raw_hex
	have = {b["contractAddress"].lower(): b.get("tokenBalance", "0x0") for b in all_tok_bal}

	# Ensure any hinted tokens appear (even if zero)
	for t in tokens_hint:
		have.setdefault(t.lower(), "0x0")

	# 2) ETH balance
	wei, ether_str = get_eth_balance(addr)

	out_lines = [addr, f"\tETH:{wei}:{ether_str}"]

	# 3) Expand tokens: only non-zero by default, but keep hinted tokens even if zero
	def is_nonzero(hexv: str) -> bool:
		try:
			return int(hexv, 16) != 0
		except Exception:
			return False

	# Keep order: hinted tokens first (their given order), then other discovered non-zero tokens sorted by address
	ordered_contracts = []
	seen = set()

	# Hinted first
	for t in tokens_hint:
		k = t.lower()
		if k in have and k not in seen:
			ordered_contracts.append(k)
			seen.add(k)

	# Others (non-zero only)
	for k, hexv in have.items():
		if k not in seen and is_nonzero(hexv):
			ordered_contracts.append(k)
			seen.add(k)

	# 4) Write token lines
	for k in ordered_contracts:
		raw_hex = have.get(k, "0x0") or "0x0"
		raw_int = int(raw_hex, 16) if raw_hex else 0
		decimals, symbol = get_token_metadata(k)
		human = raw_int / (10 ** decimals) if decimals >= 0 else raw_int
		human_str = f"{human:.18f}".rstrip("0").rstrip(".") if human != 0 else "0"
		# restore original checksum if hinted, else use lower-case hex form
		pretty_addr = k
		for t in tokens_hint:
			if t.lower() == k:
				pretty_addr = t
				break
		out_lines.append(f"\t{pretty_addr}:{raw_int}:{human_str}:{symbol}(decimals {decimals})")

	return "\n".join(out_lines) + "\n"

def main():
	# Prep files
	if not os.path.exists(INPUT_FILE):
		print(f"Input file '{INPUT_FILE}' not found.", file=sys.stderr)
		sys.exit(1)
	# Truncate output
	open(OUTPUT_FILE, "w").close()
	open(ERROR_FILE, "w").close()

	# Load non-empty lines
	with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
		lines = [ln for ln in f if ln.strip()]
	total = len(lines)

	with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex, tqdm(total=total, desc="Processing", unit="addr") as pbar:
		futures = {ex.submit(process_one, ln): ln for ln in lines}
		for fut in as_completed(futures):
			try:
				res = fut.result()
				with write_lock:
					with open(OUTPUT_FILE, "a", encoding="utf-8") as o:
						o.write(res)
			except Exception as e:
				bad = futures[fut].strip()
				msg = f"{bad} :: {repr(e)}"
				with write_lock:
					with open(ERROR_FILE, "a", encoding="utf-8") as er:
						er.write(msg + "\n")
			finally:
				pbar.update(1)
				pbar.refresh()

	# Beep on stderr to signal completion in many terminals
	print("\a", end="", file=sys.stderr)

if __name__ == "__main__":
	main()
