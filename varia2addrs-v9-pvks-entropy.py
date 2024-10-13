#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
import base58
import sys
from multiprocessing import Process, Manager, Pool
from tqdm import tqdm
from functools import partial

# Funkcje konwertujące klucze
def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes).decode()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

# Funkcja przetwarzająca klucz
def process_key(k, queue):
	k = k.strip()
	results = []

	# Przetwarzanie klucza na portfel
	try:
		wallet1 = HDWallet(symbol=BTC).from_private_key(private_key=k)
		results.extend(generate_output(wallet1))
	except:
		pass

	try:
		wallet2 = HDWallet(symbol=BTC).from_entropy(entropy=k[0:32])
		results.extend(generate_output(wallet2))
	except:
		pass

	try:
		wallet3 = HDWallet(symbol=BTC).from_entropy(entropy=k[32:64])
		results.extend(generate_output(wallet3))
	except:
		pass

	# Jeśli wyniki istnieją, dodajemy je do kolejki
	if results:
		queue.put("\n".join(results))

def generate_output(wallet):
	"""Generuje listę wyników z instancji portfela."""
	output = []
	pvk = wallet.private_key()
	wif = pvk_to_wif2(pvk)
	output.append(wif)
	output.append(wallet.wif())
	output.append(wallet.p2pkh_address())
	output.append(wallet.p2sh_address())
	output.append(wallet.p2wpkh_address())
	output.append(wallet.p2wpkh_in_p2sh_address())
	output.append(wallet.p2wsh_address())
	output.append(wallet.p2wsh_in_p2sh_address())
	output.append("")  # Pusta linia rozdzielająca kolejne wpisy
	return output

def writer_process(queue, filename):
	"""Proces zapisujący wyniki do pliku."""
	with open(filename, 'w') as outfile:
		while True:
			try:
				result = queue.get()
				if result == "DONE":
					break  # Przerywamy, gdy wszystkie procesy zakończą przetwarzanie
				outfile.write(result + "\n")
				outfile.flush()  # Zapewniamy, że dane są zapisywane natychmiast
			except Exception:
				break

def main():
	# Ustawienia Manager.Queue
	with Manager() as manager:
		queue = manager.Queue()

		# Tworzymy proces zapisu
		writer = Process(target=writer_process, args=(queue, 'output.txt'))
		writer.start()  # Uruchamiamy proces zapisu

		# Wczytanie linii z pliku
		print('Reading...', flush=True)
		lines = open('input.txt', 'r').read().splitlines()

		# Sprawdzamy, czy lista nie jest pusta
		if not lines:
			print("Plik wejściowy jest pusty.", file=sys.stderr)
			return

		# Użycie multiprocessing.Pool do równoległego przetwarzania
		pool = Pool(processes=24)  # Liczba procesów w puli (dostosuj w razie potrzeby)

		# Tworzymy funkcję częściową z domyślnym argumentem `queue`
		process_func = partial(process_key, queue=queue)

		# Równoległe przetwarzanie kluczy z paskiem postępu
		print('Writing...', flush=True)
		for _ in tqdm(pool.imap_unordered(process_func, lines), total=len(lines), desc="Przetwarzanie kluczy"):
			pass

		# Zamykamy pulę procesów i czekamy na zakończenie
		pool.close()
		pool.join()

		# Powiadomienie o zakończeniu
		queue.put("DONE")  # Informujemy proces zapisu, że przetwarzanie zakończono
		writer.join()  # Czekamy na zakończenie procesu zapisu

if __name__ == "__main__":
	main()
