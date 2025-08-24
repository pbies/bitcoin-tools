#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv, os, time, json, threading, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests
from tqdm import tqdm

RPC_URL = os.environ.get("XMR_RPC_URL", "http://127.0.0.1:18083/json_rpc")
RPC_USER = os.environ.get("XMR_RPC_USER", "user")
RPC_PASS = os.environ.get("XMR_RPC_PASS", "pass")
WALLET_DIR = os.environ.get("XMR_WALLET_DIR", "/mnt/c/2/xmr_watch_wallets")
WAL_PASS = ""
DAEMON_ADDR = "127.0.0.1:18081"
INPUT_CSV = os.environ.get("XMR_INPUT", "output.txt")
OUT_CSV = os.environ.get("XMR_OUT", "balances.csv")
THREADS = int(os.environ.get("XMR_THREADS", "4"))
REFRESH_TIMEOUT = int(os.environ.get("XMR_REFRESH_TIMEOUT", "900"))  # s
CLI_BIN = "./monero-wallet-cli"

session = requests.Session()
session.auth = (RPC_USER, RPC_PASS)
session.headers.update({"Content-Type": "application/json"})

lock = threading.Lock()
Path(WALLET_DIR).mkdir(parents=True, exist_ok=True)

def rpc(method, params=None, timeout=120):
	payload = {"jsonrpc": "2.0", "id": "0", "method": method}
	if params is not None:
		payload["params"] = params
	r = session.post(RPC_URL, data=json.dumps(payload), timeout=timeout)
	r.raise_for_status()
	resp = r.json()
	if "error" in resp:
		raise RuntimeError(f"RPC {method} error: {resp['error']}")
	return resp["result"]

def open_wallet(name, password=""):
	res = rpc("open_wallet", {"filename": name, "password": password})
	rpc("set_daemon", {"address": "http://127.0.0.1:18081", "trusted": True})
	return res

def close_wallet():
	try:
		rpc("close_wallet")
	except Exception:
		pass

def create_watch_only_via_cli(name: str, address: str, viewkey: str, restore_height: int = 0):
	wallet_path = str(Path(WALLET_DIR) / name)
	cmd = [
		CLI_BIN,
		"--generate-from-keys", wallet_path,
		"--restore-height", str(restore_height),
		"--password", WAL_PASS,
		"--daemon-address", DAEMON_ADDR,
		"--trusted-daemon",
	]
	# wstrzykujemy dane interaktywnie
	stdin_data = f"{address}\n{viewkey}\n\n"
	cp = subprocess.run(cmd, input=stdin_data, text=True,
	                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if cp.returncode != 0:
		raise RuntimeError(f"monero-wallet-cli failed:\n{cp.stdout}")

def ensure_watch_wallet(name, address, viewkey):
	keys = Path(WALLET_DIR) / f"{name}.keys"
	main = Path(WALLET_DIR) / name
	if not (keys.exists() or main.exists()):
		generate_watch_only(name, address, viewkey, WAL_PASS)

def generate_watch_only(filename, address, viewkey, password=""):
	params = {
		"restore_height": 0,
		"filename": filename,
		"address": address,
		"viewkey": viewkey,     # PRYWATNY view key
		"password": password,
		"autosave_current": True
	}
	return rpc("generate_from_keys", params)

def get_balance():
	# zwraca atomic units (piconero). 1 XMR = 1e12
	res = rpc("get_balance", {"account_index": 0})
	return res.get("balance", 0), res.get("unlocked_balance", 0)

def refresh_until_synced(timeout=REFRESH_TIMEOUT):
	start = time.time()
	while True:
		rpc("refresh")
		# proste odczekanie; bardziej elegancko: get_height vs daemon height (get_height/get_info)
		time.sleep(2)
		if time.time() - start > timeout:
			break

def atomic_to_xmr(amt):
	return amt / 1_000_000_000_000

def process_entry(idx, address, viewkey):
	spendkey = '0'*64
	name = f"watch_{idx}"
	wpath = Path(WALLET_DIR) / name
	try:
		if not (wpath.with_suffix(".keys").exists() or wpath.exists()):
			ensure_watch_wallet(name, address, viewkey)
			open_wallet(name, "")              # <<< DODAJ TO
		else:
			open_wallet(name, "")

		refresh_until_synced()
		bal, unlocked = get_balance()
		row = [address, atomic_to_xmr(bal), atomic_to_xmr(unlocked)]
	except Exception as e:
		row = [address, "ERROR", str(e)]
	finally:
		close_wallet()

	with lock, open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
		csv.writer(f).writerow(row)
	return row

def main():
	# nagłówek outputu
	#if not Path(OUT_CSV).exists():
	with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
		cw = csv.writer(f)
		cw.writerow(["address", "balance_xmr", "unlocked_xmr"])

	tasks = []
	with open(INPUT_CSV, newline="", encoding="utf-8") as f:
		cr = csv.DictReader(f)
		entries = [(i, r["address"].strip(), r["view_key"].strip()) for i, r in enumerate(cr, 1)]

	with ThreadPoolExecutor(max_workers=THREADS) as ex:
		futs = {ex.submit(process_entry, i, addr, vkey): (i) for i, addr, vkey in entries}
		for _ in tqdm(as_completed(futs), total=len(futs), desc="Scanning"):
			pass

if __name__ == "__main__":
	main()
