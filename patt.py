#!/usr/bin/env python3

import os

# works! SLOW

# frazy do wyszukania w plikach .txt
search_terms = open('patt.txt','r').read().splitlines()
output_file = "results.txt"

with open(output_file, "w", encoding="utf-8") as out:
	for root, _, files in os.walk("."):
		for fname in files:
			if fname.lower().endswith(".txt"):
				path = os.path.join(root, fname)
				print(path)
				try:
					with open(path, "r", encoding="utf-8", errors="ignore") as f:
						for lineno, line in enumerate(f, 1):
							if any(term in line for term in search_terms):
								out.write(f"{path}:{lineno}: {line}")
				except Exception as e:
					print(f"Nie udało się odczytać {path}: {e}")

print(f"Wyniki zapisane do {output_file}")
