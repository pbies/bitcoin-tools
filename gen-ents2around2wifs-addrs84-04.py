#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations.bip84 import BIP84Derivation
from hdwallet.entropies import BIP39Entropy
from hdwallet.hds import BIP84HD
from multiprocessing import Pool, Lock, Manager
from tqdm import tqdm
import base58
import os
import sys

# Przekształcenie klucza prywatnego (hex) do formatu WIF
def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

# Stałe
OFFSETS = [-65536, -65535, -31337, -1000, -100, -64, 0, 1, 64, 100, 1000, 31337, 65535, 65536]
th = 15  # liczba wątków

# Funkcja generująca dane dla jednego klucza

def go(args):
	x, lock = args
	result_lines = []
	# Sprawdzenie zakresu
	if x <= 0 or x >= (1 << 128):
		return None

	entropy_hex = hex(x)[2:].zfill(32)

	for index in range(0, 101):  # ograniczamy do pierwszych 5 adresów (można zwiększyć)
		try:
			derivation = BIP84Derivation().from_path(f"m/84'/0'/0'/0/{index}")
			hdwallet = (
				HDWallet(cryptocurrency=BTC, hd=BIP84HD)
				.from_entropy(entropy=BIP39Entropy(entropy_hex))
				.from_derivation(derivation)
			)

			pvk = hdwallet.private_key()
			wif = pvk_to_wif2(pvk)

			line = f"{entropy_hex}\n{wif}\n{hdwallet.wif()}\n"
			line += f"{hdwallet.address('P2PKH')}\n{hdwallet.address('P2SH')}\n"
			line += f"{hdwallet.address('P2TR')}\n{hdwallet.address('P2WPKH')}\n"
			line += f"{hdwallet.address('P2WPKH-In-P2SH')}\n{hdwallet.address('P2WSH')}\n"
			line += f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"

			result_lines.append(line)

		except Exception:
			continue

	# Zapis do pliku w synchronizacji
	if result_lines:
		with lock:
			with open("output.txt", "a") as outfile:
				outfile.writelines(result_lines)
				outfile.flush()

if __name__ == '__main__':
	os.system('cls||clear')
	print('Getting ready...', flush=True)

	# Przygotowanie danych wejściowych
	i_range = list(range(2, 65537))
	j_range = list(range(2, 129))

	raw_inputs = set()
	for i in tqdm(i_range, desc="Generating inputs"):
		for j in j_range:
			base_val = pow(i, j, 1 << 128)
			for z in OFFSETS:
				candidate = base_val + z
				if 0 < candidate < (1 << 128):
					raw_inputs.add(candidate)

	print(f"Total unique inputs: {len(raw_inputs)}")
	print('Writing...', flush=True)

	# Usunięcie starego pliku wynikowego
	if os.path.exists("output.txt"):
		os.remove("output.txt")

	with Manager() as manager:
		lock = manager.Lock()
		args_list = [(x, lock) for x in raw_inputs]

		with Pool(processes=th) as pool:
			list(tqdm(pool.imap_unordered(go, args_list, chunksize=500), total=len(args_list)))

	print('\aDone.', file=sys.stderr)
