#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
from libcrypto import Wallet
import sys, os
from queue import Queue
from threading import Thread, Lock
import time
from tqdm import tqdm
from collections import deque

CHUNK_SIZE = 1000
OUTPUT_QUEUE_SIZE = 1000

class ProgressTracker:
	"""Klasa do śledzenia postępu z synchronizacją wielowątkową"""
	def __init__(self, total_lines):
		self.total = total_lines
		self.processed = 0
		self.failed = 0
		self.lock = Lock()
		self.pbar = tqdm(total=total_lines, unit=' lines', desc='Przetwarzanie',
						bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]',
						colour='green')
	
	def update(self, count, failed_count=0):
		"""Aktualizuje postęp - bezpieczna dla wątków"""
		with self.lock:
			self.processed += count
			self.failed += failed_count
			self.pbar.update(count)
			self.pbar.set_postfix({
				'Sukces': f"{self.processed:,}/{self.total:,}",
				'Błędy': f"{self.failed:,}"
			})
	
	def close(self):
		"""Zamyka pasek postępu"""
		self.pbar.close()
	
	def get_stats(self):
		"""Zwraca statystyki"""
		with self.lock:
			return self.processed, self.failed, self.total

def count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def worker(input_queue, output_queue, progress_tracker):
	"""Worker thread processing keys"""
	while True:
		lines = input_queue.get()
		if lines is None:  # Sentinel value
			break
			
		results = []
		successful = 0
		failed = 0
		
		for line in lines:
			line = line.strip()
			if not line:
				continue
				
			try:
				wallet = Wallet(line)
				# All addresses in one go
				btc_addrs = [
					wallet.get_address(coin="bitcoin", address_type="p2pkh"),
					wallet.get_address(coin="bitcoin", address_type="p2sh-p2wpkh"),
					wallet.get_address(coin="bitcoin", address_type="p2wpkh"),
				]
				ltc_addrs = [
					wallet.get_address(coin="litecoin", address_type="p2pkh"),
					wallet.get_address(coin="litecoin", address_type="p2sh-p2wpkh"),
					wallet.get_address(coin="litecoin", address_type="p2wpkh"),
				]
				
				results.append(f"{line}\n" + "\n".join(btc_addrs) + "\n" + 
							 "\n".join(ltc_addrs) + "\n\n")
				successful += 1
			except Exception:
				failed += 1
				continue
		
		# Aktualizuj postęp
		if successful > 0 or failed > 0:
			progress_tracker.update(successful, failed)
		
		if results:
			output_queue.put(''.join(results))
		input_queue.task_done()

def writer_thread(output_queue, output_file, stats_queue):
	"""Dedicated writer thread with statistics"""
	written_chunks = 0
	written_bytes = 0
	
	with open(output_file, 'a', buffering=1024*1024*32) as f:
		last_flush_time = time.time()
		
		while True:
			try:
				data = output_queue.get(timeout=1)
				if data is None:
					break
				
				f.write(data)
				written_bytes += len(data)
				written_chunks += 1
				
				# Flush co 2 sekundy lub co 8MB danych
				current_time = time.time()
				if current_time - last_flush_time > 2 or written_bytes > 8 * 1024 * 1024:
					f.flush()
					last_flush_time = current_time
					written_bytes = 0
				
				output_queue.task_done()
				
			except Exception:
				# Timeout, sprawdź czy mamy kontynuować
				continue
	
	# Prześlij statystyki zapisu
	stats_queue.put(('writer', written_chunks))

def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	if not os.path.exists(input_file):
		print(f"Błąd: Plik {input_file} nie istnieje!", file=sys.stderr)
		sys.exit(1)
	
	# Obliczanie całkowitej liczby linii
	print(f"Liczenie linii w pliku {input_file}...")
	total_lines = count_lines(input_file)
	
	print(f"\n{'='*60}")
	print(f"PRZETWARZANIE KLUCZY PRYWATNYCH")
	print(f"{'='*60}")
	print(f"Plik wejściowy:  {input_file}")
	print(f"Plik wynikowy:   {output_file}")
	print(f"Liczba kluczy:   {total_lines:,}")
	print(f"Rozmiar chunka:  {CHUNK_SIZE:,} kluczy")
	print(f"{'='*60}\n")
	
	# Inicjalizacja tracker postępu
	progress_tracker = ProgressTracker(total_lines)
	
	# Czyszczenie pliku wyjściowego
	open(output_file, 'w').close()
	
	# Kolejki
	input_queue = Queue(maxsize=50)
	output_queue = Queue(maxsize=100)
	stats_queue = Queue()  # Dla statystyk
	
	# Start writer thread
	writer = Thread(target=writer_thread, args=(output_queue, output_file, stats_queue))
	writer.daemon = True
	writer.start()
	
	# Tworzenie wątków roboczych
	num_workers = min(32, (os.cpu_count() or 4) * 4)
	print(f"Uruchamianie {num_workers} wątków roboczych...")
	
	# Licznik czasu
	start_time = time.time()
	
	try:
		with ThreadPoolExecutor(max_workers=num_workers) as executor:
			# Submit worker tasks
			futures = []
			for _ in range(num_workers):
				future = executor.submit(worker, input_queue, output_queue, progress_tracker)
				futures.append(future)
			
			# Odczyt i karmienie danych
			print("Rozpoczynanie przetwarzania...\n")
			with open(input_file, 'r', buffering=1024*1024*16) as f:
				chunk = []
				for line_num, line in enumerate(f, 1):
					chunk.append(line)
					if len(chunk) >= CHUNK_SIZE:
						input_queue.put(chunk)
						chunk = []
				
				if chunk:
					input_queue.put(chunk)
			
			# Sygnalizuj wątkom aby się zatrzymały
			for _ in range(num_workers):
				input_queue.put(None)
			
			# Czekaj na zakończenie wątków
			print("\nOczekiwanie na zakończenie przetwarzania...")
			for future in as_completed(futures):
				future.result()
		
		# Sygnalizuj writerowi aby się zatrzymał
		output_queue.put(None)
		writer.join()
		
		# Zakończenie
		progress_tracker.close()
		
		# Oblicz czas wykonania
		end_time = time.time()
		elapsed_time = end_time - start_time
		
		# Pobierz statystyki
		processed, failed, total = progress_tracker.get_stats()
		
		# Pobierz statystyki zapisu
		writer_chunks = 0
		while not stats_queue.empty():
			try:
				stat_type, value = stats_queue.get_nowait()
				if stat_type == 'writer':
					writer_chunks = value
			except:
				pass
		
		print(f"\n{'='*60}")
		print(f"PRZETWARZANIE ZAKOŃCZONE!")
		print(f"{'='*60}")
		print(f"Czas wykonania:	  {elapsed_time:.2f} sekund")
		print(f"Przetworzono:		 {processed:,} kluczy")
		print(f"Nieudane:			{failed:,} kluczy")
		print(f"Łącznie:			 {total:,} kluczy")
		if elapsed_time > 0:
			print(f"Prędkość:			{processed/elapsed_time:.2f} kluczy/sekundę")
		if processed > 0:
			success_rate = (processed / (processed + failed)) * 100
			print(f"Skuteczność:		 {success_rate:.2f}%")
		print(f"Chunków zapisanych:   {writer_chunks:,}")
		print(f"Plik wynikowy:	   {output_file}")
		print(f"{'='*60}")
		
	except KeyboardInterrupt:
		print("\n\nPrzerwano przez użytkownika!")
		progress_tracker.close()
	except Exception as e:
		print(f"\n\nBłąd podczas przetwarzania: {e}")
		progress_tracker.close()
	
	# Dźwięk zakończenia
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
