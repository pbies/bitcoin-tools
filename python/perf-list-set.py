#!/usr/bin/env python3

import time
import random
import matplotlib.pyplot as plt

def test_search_performance(max_size=1_000_000, step=100_000, repetitions=100):
	"""
	Testuje czas wyszukiwania elementu w liście i w secie
	dla różnych rozmiarów struktur danych.
	"""
	sizes = list(range(step, max_size + 1, step))
	list_times = []
	set_times = []

	print("Przygotowywanie danych i testowanie wydajności...\n")
	print("      Rozmiar   |   Lista (ms)  |   Set (ms)    | Przyspieszenie")
	print("-" * 70)

	for size in sizes:
		# Generujemy dane
		data_list = list(range(size))
		data_set = set(data_list)
		
		# Element do wyszukania – najgorszy przypadek dla listy (na końcu lub nie ma go)
		# Wybieramy element, który istnieje (żeby set też musiał go szukać)
		search_element = size // 2  # element w środku

		# === Test dla listy ===
		start = time.perf_counter()
		for _ in range(repetitions):
			result = search_element in data_list  # operator 'in' dla listy
		end = time.perf_counter()
		list_time = (end - start) * 1000 / repetitions  # średni czas w ms

		# === Test dla seta ===
		start = time.perf_counter()
		for _ in range(repetitions):
			result = search_element in data_set
		end = time.perf_counter()
		set_time = (end - start) * 1000 / repetitions  # średni czas w ms

		list_times.append(list_time)
		set_times.append(set_time)

		speedup = list_time / set_time if set_time > 0 else float('inf')
		print(f"{size:10,}	|   {list_time:8.4f}	|   {set_time:8.4f}	| {speedup:6.1f}x")

	# Wykres
	plt.figure(figsize=(10, 6))
	plt.plot(sizes, list_times, 'o-', label='Lista (list)', color='red')
	plt.plot(sizes, set_times, 's-', label='Zbiór (set)', color='green')
	plt.xlabel('Rozmiar struktury danych')
	plt.ylabel('Średni czas wyszukiwania [ms]')
	plt.title('Porównanie prędkości operacji "in" – list vs set')
	plt.legend()
	plt.grid(True, alpha=0.3)
	plt.yscale('log')  # skala logarytmiczna – różnica jest ogromna!
	plt.tight_layout()
	plt.show()

if __name__ == "__main__":
	# Możesz dostosować parametry:
	# max_size – maksymalna wielkość struktury
	# step – co ile elementów testujemy
	# repetitions – ile razy powtarzamy wyszukiwanie (dla lepszej precyzji)
	test_search_performance(max_size=1_000_000, step=100_000, repetitions=200)
