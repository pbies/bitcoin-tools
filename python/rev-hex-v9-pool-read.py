#!/usr/bin/env python3
import os
import sys
import binascii
from multiprocessing import Pool
from tqdm import tqdm

# Worker: dostaje listę linii (bytes), zwraca (wynik_bytes, ile_bajtow_wejscia)
def go_batch(lines):
	out_parts = []
	in_bytes = 0

	for raw in lines:
		in_bytes += len(raw)

		# usuń tylko końcowy \n / \r\n do obróbki; progres liczony z raw (oryginalne bajty)
		line = raw.rstrip(b"\r\n")
		if not line:
			continue

		try:
			# h2 = reverse(bytes.fromhex(line)).hex() ale bez decode()
			b = binascii.unhexlify(line)		# line = ASCII hex w bytes
			h2 = binascii.hexlify(b[::-1])		# bytes

		except Exception:
			continue

		# Operacje na hex-stringu jako bytes (ASCII)
		h1 = line[::-1]
		tmp1 = line[0::2]
		tmp2 = line[1::2]
		h3 = tmp1 + tmp2
		h4 = tmp2 + tmp1

		out_parts.append(line + b"\n" + h1 + b"\n" + h2 + b"\n" + h3 + b"\n" + h4 + b"\n")

	return (b"".join(out_parts), in_bytes)

def iter_batches(fin, batch_lines=20000):
	buf = []
	for raw in fin:
		buf.append(raw)
		if len(buf) >= batch_lines:
			yield buf
			buf = []
	if buf:
		yield buf

def main():
	infile = "input.txt"
	outfile = "output.txt"

	th = min(24, os.cpu_count() or 1)	# podbijaj do liczby rdzeni
	batch_lines = 20000				# im większe, tym mniej narzutu IPC; testuj 10k–100k

	size = os.path.getsize(infile)

	with open(infile, "rb") as fin, open(outfile, "wb", buffering=1024 * 1024) as fout:
		with tqdm(total=size, unit="B", unit_scale=True, unit_divisor=1024) as pbar:
			with Pool(th) as pool:
				for out_bytes, in_bytes in pool.imap_unordered(go_batch, iter_batches(fin, batch_lines=batch_lines), chunksize=1):
					if out_bytes:
						fout.write(out_bytes)
					pbar.update(in_bytes)

	print("\a", end="", file=sys.stderr)

if __name__ == "__main__":
	main()
