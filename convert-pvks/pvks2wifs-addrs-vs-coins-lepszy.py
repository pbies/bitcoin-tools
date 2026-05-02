#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from libcrypto import Wallet
import os, sys
from itertools import islice
from tqdm import tqdm
import math

CHUNK_LINES = 1000  # Zwiększony rozmiar chunka
OUTPUT_BUFFER_SIZE = 1000  # Buffer dla zapisu

def count_lines(file_path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(file_path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(file_path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(file_path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def process_chunk(lines):
	"""Przetwarza chunk linii - zoptymalizowana wersja"""
	results = []
	for line in lines:
		line = line.decode('utf-8', errors='ignore').strip()
		if not line:
			continue
			
		try:
			wallet = Wallet(line)
			# Bitcoin addresses
			btc_p2pkh = wallet.get_address(coin="bitcoin", address_type="p2pkh")
			btc_p2sh = wallet.get_address(coin="bitcoin", address_type="p2sh-p2wpkh")
			btc_p2wpkh = wallet.get_address(coin="bitcoin", address_type="p2wpkh")
			
			# Litecoin addresses
			ltc_p2pkh = wallet.get_address(coin="litecoin", address_type="p2pkh")
			ltc_p2sh = wallet.get_address(coin="litecoin", address_type="p2sh-p2wpkh")
			ltc_p2wpkh = wallet.get_address(coin="litecoin", address_type="p2wpkh")
			
			# Formatowanie z góry
			results.append(f"{line}\n{btc_p2pkh}\n{btc_p2sh}\n{btc_p2wpkh}\n"
						  f"{ltc_p2pkh}\n{ltc_p2sh}\n{ltc_p2wpkh}\n\n")
		except Exception:
			continue
	
	return ''.join(results)

def chunk_reader(file_path, chunk_size=CHUNK_LINES):
	"""Generator czytający plik w chunkach"""
	with open(file_path, 'rb', buffering=1024*1024*8) as f:  # 8MB buffer
		while True:
			lines = list(islice(f, chunk_size))
			if not lines:
				break
			yield [line.rstrip(b'\n') for line in lines]

def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	if not os.path.exists(input_file):
		print(f"Error: Plik {input_file} nie istnieje!", file=sys.stderr)
		sys.exit(1)
	
	# Obliczanie całkowitej liczby chunków dla paska postępu
	print(f"Liczenie linii w pliku {input_file}...")
	total_lines = count_lines(input_file)
	total_chunks = math.ceil(total_lines / CHUNK_LINES)
	
	print(f"Przetwarzanie pliku: {input_file}")
	print(f"Całkowita liczba linii: {total_lines:,}")
	print(f"Rozmiar chunka: {CHUNK_LINES:,} linii")
	print(f"Szacowana liczba chunków: {total_chunks:,}")
	print(f"Plik wynikowy: {output_file}")
	print()
	
	# Czyszczenie outputu
	open(output_file, 'w').close()
	
	workers = max(1, cpu_count() - 1)  # Zostaw 1 core dla systemu
	print(f"Używanie {workers} procesów roboczych")
	
	# Utwórz pasek postępu
	pbar = tqdm(total=total_lines, unit=' lines', desc='Przetwarzanie', 
				bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')
	
	# Optymalizacja: większe chunki, mniej overhead
	with Pool(workers, maxtasksperchild=1000) as pool:
		with open(output_file, 'a', buffering=1024*1024*16) as f_out:  # 16MB buffer
			# Użycie map_async dla lepszej kontroli
			results = pool.imap_unordered(
				process_chunk, 
				chunk_reader(input_file),
				chunksize=10  # Mniej tasków, większe chunki
			)
			
			output_buffer = []
			buffer_size = 0
			processed_lines = 0
			
			for result in results:
				if result:
					output_buffer.append(result)
					buffer_size += len(result)
					
					# Liczba przetworzonych linii z tego chunka
					# (każda poprawna linia generuje 8 linii w wyniku)
					lines_in_result = result.count('\n\n')  # Każdy wpis kończy się \n\n
					processed_lines += lines_in_result
					
					# Aktualizuj pasek postępu
					pbar.update(lines_in_result)
					pbar.set_postfix({'Chunks': f"{processed_lines:,}/{total_lines:,}"})
					
					# Flush buffer when large enough
					if buffer_size > 1024*1024*4:  # 4MB
						f_out.write(''.join(output_buffer))
						f_out.flush()  # Wymuszamy zapis na dysk
						output_buffer.clear()
						buffer_size = 0
			
			# Flush remaining
			if output_buffer:
				f_out.write(''.join(output_buffer))
				f_out.flush()
	
	# Zamknij pasek postępu
	pbar.close()
	
	# Informacja o zakończeniu
	print(f"\n{'='*50}")
	print(f"Przetwarzanie zakończone!")
	print(f"Wyniki zapisano do: {output_file}")
	print(f"Przetworzono {processed_lines:,} kluczy prywatnych")
	print(f"{'='*50}")
	
	# Dźwięk zakończenia
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
