#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, datetime, time, glob
from tqdm import tqdm

MAGIC = b"\x02\x01\x01\x04\x20"	# 5 bytes
PAYLOAD_LEN = 32
NEED = len(MAGIC) + PAYLOAD_LEN	# 37

def process_file(path: str, chunk_size: int = 8 * 1024 * 1024) -> None:
	print(f"Processing {path}...")

	try:
		total = os.path.getsize(path)
	except OSError:
		print("File not found!")
		return

	out_path = path + ".txt"

	with open(path, "rb") as f, open(out_path, "a", buffering=1) as o:
		pbar = tqdm(total=total, unit="B", unit_scale=True)
		tail = b""
		base_offset = 0

		while True:
			chunk = f.read(chunk_size)
			if not chunk:
				break

			pbar.update(len(chunk))

			data = tail + chunk
			# base_offset = pozycja w pliku odpowiadająca data[0]
			base_offset = f.tell() - len(chunk) - len(tail)

			limit = len(data) - NEED + 1
			if limit > 0:
				for i in range(limit):
					if data[i:i + len(MAGIC)] == MAGIC:
						y = data[i + len(MAGIC): i + len(MAGIC) + PAYLOAD_LEN]
						o.write(y.hex() + "\n")

			# zostaw ogon na dopasowania przez granicę chunka
			tail = data[-(NEED - 1):] if len(data) >= (NEED - 1) else data

		pbar.close()

def main() -> None:
	os.system("cls" if os.name == "nt" else "clear")
	print("Program started: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	start_time = time.time()

	for path in glob.glob("*.dat"):
		process_file(path)

	stop_time = time.time()
	print("Program stopped: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	print(f"Execution took: {str(datetime.timedelta(seconds=stop_time - start_time))}")
	print("\a", end="", file=sys.stderr)

if __name__ == "__main__":
	main()
