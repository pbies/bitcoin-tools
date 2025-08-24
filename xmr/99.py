#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv, os, re, subprocess, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

# ======= Konfiguracja =======
INPUT_CSV	= os.environ.get("XMR_INPUT", "input.txt")
OUT_CSV		= os.environ.get("XMR_OUT", "output.csv")
THREADS		= int(os.environ.get("XMR_THREADS", "4"))
WALLET_DIR	= os.environ.get("XMR_WALLET_DIR", "/mnt/c/1/xmr_watch_wallets")
WAL_PASS	= os.environ.get("XMR_WAL_PASS", "")
DAEMON_ADDR	= os.environ.get("XMR_DAEMON_ADDR", "127.0.0.1:18081")
CLI_BIN		= os.environ.get("XMR_CLI_BIN", "./monero-wallet-cli")

# ======= Synchronizacja zapisu =======
lock = threading.Lock()
Path(WALLET_DIR).mkdir(parents=True, exist_ok=True)

def _run(args, stdin=""):
	cp = subprocess.run(args, input=stdin, text=True,
	                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return cp.returncode, cp.stdout

def _addr_from_spend(cli_bin:str, spend_hex:str) -> str:
	rc, out = _run([cli_bin, "--generate-from-spend-key", "/tmp/_probe",
	                "--log-file","/dev/null","--password","",
	                "--command","address"], stdin=spend_hex.strip()+"\n")
	if rc != 0:
		return ""
	for line in out.splitlines():
		line = line.strip()
		if len(line) >= 95 and line[0] in "4895":
			return line.split()[0]
	return ""

def ensure_wallet_exists(name, address, viewkey, spendkey,
                         restore_height, cli_bin, wallet_dir):
	from pathlib import Path
	wallet_path = Path(wallet_dir) / name
	if wallet_path.exists() or wallet_path.with_suffix(".keys").exists():
		return

	common = ["--password", "", "--offline", "--log-file", "/dev/null"]

	if spendkey:
		# pełny portfel z samego spend key
		args = [cli_bin, "--generate-from-spend-key", str(wallet_path), *common]
		stdin_data = spendkey.strip() + "\n"
	else:
		# watch-only
		args = [cli_bin, "--generate-from-view-key", str(wallet_path), *common]
		stdin_data = f"{address.strip()}\n{(viewkey or '').strip()}\n"

	if restore_height is not None:
		args += ["--restore-height", str(restore_height)]

	rc, out = run_cli(args, stdin_data, timeout=30)
	if rc != 0:
		raise RuntimeError(f"[{name}] create failed:\n{out}")

def run_cli(args:list, stdin_data:str="", timeout:int=200):
	"""
	Uruchamia monero-wallet-cli z timeoutem.
	Zwraca (rc, stdout). Przy timeout podnosi TimeoutError (łap to wyżej).
	"""
	cp = subprocess.run(
		args,
		input=stdin_data,
		text=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		timeout=timeout
	)
	return cp.returncode, cp.stdout

	# Monero przy pierwszym starcie może spytać o język – wymusimy angielski przy dalszych wywołaniach.

def parse_balance(output:str):
	"""
	Szuka linii w formacie:
	  Balance: X, unlocked balance: Y
	Zwraca (X, Y) w XMR jako stringi zachowując precyzję.
	"""
	# przykład: Balance: 0.000000000000, unlocked balance: 0.000000000000
	m = re.search(r"Balance:\s*([0-9]+\.[0-9]+|[0-9]+)\s*,\s*unlocked balance:\s*([0-9]+\.[0-9]+|[0-9]+)", output, re.IGNORECASE)
	if not m:
		# alternatywnie spotyka się "Currently selected account: [0] ... Balance: ... unlocked balance: ..."
		m = re.search(r"unlocked balance:\s*([0-9]+\.[0-9]+|[0-9]+)", output, re.IGNORECASE)
		if m:
			ub = m.group(1)
			# jeżeli tylko unlocked znaleźliśmy, spróbujmy też plain Balance:
			m2 = re.search(r"Balance:\s*([0-9]+\.[0-9]+|[0-9]+)", output, re.IGNORECASE)
			if m2:
				return (m2.group(1), ub)
		raise ValueError("Nie udało się sparsować wyniku 'balance'")
	return (m.group(1), m.group(2))

def refresh_and_get_balance(name, cli_bin, wallet_dir, daemon_addr, do_refresh=True):
	from pathlib import Path
	wallet_path = Path(wallet_dir) / name

	args = [cli_bin, "--wallet-file", str(wallet_path),
	        "--password", "", "--log-file", "/dev/null"]

	if do_refresh:
		args += ["--daemon-address", daemon_addr, "--trusted-daemon",
		         "--command", "refresh"]

	# zawsze rób balance i wyjście
	args += ["--command", "balance", "--command", "exit"]

	# dłuższy timeout gdy refresh
	timeout = int(os.environ.get("XMR_REFRESH_TIMEOUT", "1800" if do_refresh else "30"))

	rc, out = run_cli(args, timeout=timeout)
	if rc != 0:
		raise RuntimeError(f"[{name}] balance failed:\n{out}")
	return parse_balance(out)

def process_row(idx:int, row:dict):
	"""
	Przetwarza pojedynczy wpis z CSV.
	Zakłada kolumny: address, view_key, spend_key (opcjonalnie), restore_height (opcjonalnie).
	Zwraca listę dla CSV wynikowego.
	"""
	address = (row.get("address") or "").strip()
	viewkey = (row.get("view_key") or row.get("private_view_key") or "").strip()
	spendkey = (row.get("spend_key") or row.get("private_spend_key") or "").strip()
	rh_str = (row.get("restore_height") or "").strip()
	restore_height = int(rh_str) if rh_str.isdigit() else None

	if not address or not viewkey:
		return [address or "(empty)", "ERROR", "Brak address/view_key w wierszu"]

	name = f"xmr_{idx:06d}"
	try:
		ensure_wallet_exists(name, address, viewkey, spendkey, restore_height, CLI_BIN, WALLET_DIR)
		DO_REFRESH = os.environ.get("XMR_NO_REFRESH", "") == ""
		bal, unlk = refresh_and_get_balance(name, CLI_BIN, WALLET_DIR, DAEMON_ADDR, do_refresh=DO_REFRESH)
		out = [address, bal, unlk]
	except Exception as e:
		out = [address, "ERROR", str(e)]

	# bezpieczny zapis do wspólnego CSV
	with lock:
		with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
			csv.writer(f).writerow(out)
	return out

def main():
	# Napisz nagłówek wyniku
	with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
		cw = csv.writer(f)
		cw.writerow(["address", "balance_xmr", "unlocked_xmr"])

	# Wczytaj wejście
	with open(INPUT_CSV, newline="", encoding="utf-8") as f:
		cr = csv.DictReader(f)
		rows = list(cr)

	# Wielowątkowe przetwarzanie
	with ThreadPoolExecutor(max_workers=THREADS) as ex:
		futs = {ex.submit(process_row, i, r): i for i, r in enumerate(rows, 1)}
		for _ in tqdm(as_completed(futs), total=len(futs), desc="Scanning"):
			pass

if __name__ == "__main__":
	main()
