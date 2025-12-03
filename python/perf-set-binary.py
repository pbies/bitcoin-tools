#!/usr/bin/env python3

import time
import random
import bisect
import matplotlib.pyplot as plt

def benchmark_binary_search_vs_set(
	max_size=2_000_000,
	step=200_000,
	repetitions=1000,
	search_cases='middle'  # 'middle', 'worst', 'random'
):
	sizes = list(range(step, max_size + 1, step))
	
	binary_times = []
	set_times = []

	print(f"{'Rozmiar':>12} {'Binary search':>16} {'Set':>14} {'Przyspieszenie':>16}")
	print("-" * 62)

	for size in sizes:
		# Przygotowanie posortowanej listy i seta
		data_list = list(range(size))		   # już posortowana
		data_set = set(data_list)

		# Wybór elementu do wyszukania
		if search_cases == 'middle':
			element = size // 2
		elif search_cases == 'worst':
			element = size - 1					 # najgorszy przypadek dla binary search
		else:  # random
			element = random.randint(0, size - 1)

		# === Binary search (używamy wbudowanego bisect) ===
		start = time.perf_counter()
		for _ in range(repetitions):
			idx = bisect.bisect_left(data_list, element)
			found = idx < len(data_list) and data_list[idx] == element
		binary_time = (time.perf_counter() - start) * 1_000 / repetitions  # ms

		# === Set ===
		start = time.perf_counter()
		for _ in range(repetitions):
			_ = element in data_set
		set_time = (time.perf_counter() - start) * 1_000 / repetitions

		binary_times.append(binary_time)
		set_times.append(set_time)

		speedup = binary_time / set_time if set_time > 0 else float('inf')

		print(f"{size:12,} {binary_time:12.5f} ms {set_time:12.5f} ms {speedup:12.0f}x")

	# === Wykres ===
	plt.figure(figsize=(11, 6))
	plt.plot(sizes, binary_times, 'o-', label='Lista + binary search', color='purple', linewidth=2.5)
	plt.plot(sizes, set_times,   's-', label='Set (hash)',		   color='green',  linewidth=2.5)

	plt.xlabel('Rozmiar danych')
	plt.ylabel('Średni czas jednego wyszukiwania [ms]')
	plt.title(f'Binary Search vs Set\n'
			  f'(wyszukiwanie: {search_cases}, {repetitions} powtórzeń)')
	plt.legend()
	plt.grid(True, alpha=0.3)
	plt.yscale('log')  # bardzo ważne – różnice są ogromne!
	plt.tight_layout()
	plt.show()

	print("\nPODSUMOWANIE:")
	print("→ Binary search na posortowanej liście: O(log n) – bardzo szybki teoretycznie")
	print("→ Set: średnio O(1) – w praktyce prawie zawsze szybszy w Pythonie")
	print("→ Przy 2 milionach elementów set jest nadal ~30–100× szybszy!")
	print("→ Dodatkowo: set nie wymaga sortowania i działa na nieposortowanych danych")

if __name__ == "__main__":
	# Możesz przetestować różne scenariusze:

	# 1. Najlepszy przypadek dla binary search (środek)
	print("=== Wyszukiwanie elementu ze środka ===")
	benchmark_binary_search_vs_set(max_size=2_000_000, step=200_000, repetitions=2000, search_cases='middle')

	# 2. Najgorszy przypadek dla binary search (ostatni element)
	print("\n=== Wyszukiwanie ostatniego elementu ===")
	benchmark_binary_search_vs_set(max_size=2_000_000, step=200_000, repetitions=2000, search_cases='worst')

	# 3. Losowe elementy
	# print("\n=== Losowe elementy ===")
	# benchmark_binary_search_vs_set(search_cases='random')
