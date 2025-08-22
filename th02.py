#!/usr/bin/env python3
import threading

# Parametry
filename = 'duzy_plik.txt'
num_threads = 4
search_term = 'ERROR'

# Funkcja przetwarzająca fragment
def process_lines(lines, thread_id, results):
	count = sum(1 for line in lines if search_term in line)
	results[thread_id] = count
	print(f"Wątek {thread_id}: znalazł {count} linii zawierających '{search_term}'")

# Główna część
with open(filename, 'r', encoding='utf-8') as f:
	lines = f.readlines()

chunk_size = len(lines) // num_threads
threads = []
results = [0] * num_threads

for i in range(num_threads):
	start = i * chunk_size
	# Ostatni wątek bierze resztę
	end = (i + 1) * chunk_size if i != num_threads - 1 else len(lines)
	thread = threading.Thread(target=process_lines, args=(lines[start:end], i, results))
	threads.append(thread)
	thread.start()

# Czekaj na wszystkie
for t in threads:
	t.join()

print("Łączny wynik:", sum(results))
