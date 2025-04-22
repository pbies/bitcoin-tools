#!/usr/bin/env python3

from tqdm import tqdm
from itertools import product
import hashlib
import multiprocessing
import sys

# Wczytanie pliku z listą
with open("list.txt", "r") as f:
    content = f.read().splitlines()

cnt = len(content)
target_hash = 'cd1f52535003618f234cf317af96ed9e45f5100949f3a0da3251957cb6acb4bf'

# Funkcja generująca kombinacje
def generate_combinations(strings, depth):
    return ("".join(combination) for combination in product(strings, repeat=depth))

# Funkcja haszująca
def sha(x):
    x = x.encode()
    return hashlib.sha256(x).hexdigest()

# Funkcja do porównania hashy
def go(line):
    s = sha(line)
    # Sprawdzenie, czy hash pasuje do szukanego
    if s == target_hash:
        with open('found.txt', 'a') as o:
            o.write(line)
            o.flush()
        # Zwracanie informacji, że znaleziono dopasowanie
        return True
    return False

def process_line(line):
    # Wywołuje funkcję `go` i zwraca, czy znaleziono dopasowanie
    result = go(line)
    return result

def run_with_progress_tracking():
    # Utworzenie puli procesów
    with multiprocessing.Pool(processes=12) as pool:
        # Generowanie kombinacji
        combinations = list(generate_combinations(content, 3))

        # Ustawienie paska postępu
        with tqdm(total=len(combinations), desc="Processing combinations") as pbar:
            # Równoległe przetwarzanie i aktualizacja paska postępu
            for result in pool.imap_unordered(process_line, combinations, chunksize=1000):
                if result:
                    print("Found match! Check 'found.txt'\a")
                    pool.terminate()  # Zatrzymanie pozostałych procesów
                    break
                pbar.update(1)

if __name__ == "__main__":
    run_with_progress_tracking()
    print('\a', end='', file=sys.stderr)
