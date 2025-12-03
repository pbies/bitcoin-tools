#!/usr/bin/env python3

import time
import random
import matplotlib.pyplot as plt

def benchmark_membership_test(max_size=1_000_000, step=100_000, repetitions=500):
	sizes = list(range(step, max_size + 1, step))
	
	results = {
		'list':  [],
		'tuple': [],
		'set':   [],
		'dict_keys': []
	}

	print(f"{'Rozmiar':>12} | {'Lista':>10} | {'Tuple':>10} | {'Set':>10} | {'Dict (klucze)':>14} | Przyspieszenie")
	print("-" * 90)

	for size in sizes:
		# Przygotowanie danych
		data_list  = list(range(size))
		data_tuple = tuple(data_list)
		data_set   = set(data_list)
		data_dict  = {i: None for i in data_list}  # słownik z kluczami 0..size-1

		# Element do wyszukania – w środku (istnieje we wszystkich strukturach)
		search_element = size // 2

		# === Testy ===
		# Lista
		start = time.perf_counter()
		for _ in range(repetitions):
			_ = search_element in data_list
		list_time = (time.perf_counter() - start) * 1000 / repetitions

		# Tuple
		start = time.perf_counter()
		for _ in range(repetitions):
			_ = search_element in data_tuple
		tuple_time = (time.perf_counter() - start) * 1000 / repetitions

		# Set
		start = time.perf_counter()
		for _ in range(repetitions):
			_ = search_element in data_set
		set_time = (time.perf_counter() - start) * 1000 / repetitions

		# Dict – sprawdzamy przynależność klucza
		start = time.perf_counter()
		for _ in range(repetitions):
			_ = search_element in data_dict
		dict_time = (time.perf_counter() - start) * 1000 / repetitions

		# Zapis wyników
		results['list'].append(list_time)
		results['tuple'].append(tuple_time)
		results['set'].append(set_time)
		results['dict_keys'].append(dict_time)

		speedup = list_time / set_time if set_time > 0 else float('inf')

		print(f"{size:12,} | {list_time:10.4f} | {tuple_time:10.4f} | {set_time:10.4f} | {dict_time:14.4f} | {speedup:8.0f}x")

	# === Wykres ===
	plt.figure(figsize=(12, 7))
	plt.plot(sizes, results['list'],  'o-', label='list',  color='red',   linewidth=2)
	plt.plot(sizes, results['tuple'], 'x--', label='tuple', color='orange', linewidth=2)
	plt.plot(sizes, results['set'],   's-', label='set',   color='green',  linewidth=2)
	plt.plot(sizes, results['dict_keys'], 'd-', label='dict (klucze)', color='blue', linewidth=2)

	plt.xlabel('Rozmiar struktury danych')
	plt.ylabel('Średni czas operacji "in" [ms]')
	plt.title('Porównanie prędkości wyszukiwania przynależności\nlist vs tuple vs set vs dict (klucze)')
	plt.legend()
	plt.grid(True, alpha=0.3)
	plt.yscale('log')  # skala logarytmiczna – bo różnice są gigantyczne
	plt.tight_layout()
	plt.show()

	print("\nWniosek:")
	print("→ set i dict (sprawdzanie klucza) mają prawie identyczną, stałą prędkość O(1)")
	print("→ list i tuple mają liniową złożoność O(n) – przy milionie elementów set jest >100 000× szybszy!")

if __name__ == "__main__":
	benchmark_membership_test(
		max_size=1_000_000,
		step=100_000,
		repetitions=500  # więcej powtórzeń = dokładniejsze wyniki
	)
