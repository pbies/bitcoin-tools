#!/usr/bin/env python3

import sys
import os
import datetime
import time

def main():
	global start_msg, start_time
	
	os.system('cls' if os.name == 'nt' else 'clear')
	print(__file__)
	
	start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time = time.time()

	if len(sys.argv) < 3:
		print("Użycie: python script.py <plik1> <plik2>")
		print("gdzie: plik1 - lista wzorców do znalezienia")
		print("	   plik2 - plik w którym szukamy")
		sys.exit(1)

	try:
		# Wczytaj wszystkie wzorce z pliku1
		with open(sys.argv[1], 'r') as f:
			patterns = [line.rstrip('\n') for line in f.readlines()]
		
		print(f"Szukam {len(patterns)} wzorców w pliku {sys.argv[2]}")
		
		# Wczytaj cały plik2
		with open(sys.argv[2], 'r') as i:
			lines_i = [line.rstrip('\n') for line in i.readlines()]
		
		found_count = 0
		
		# Przeszukuj plik2 fragmentami po 11 linii
		for idx in range(0, len(lines_i), 11):
			# Pobierz fragment 11 linii (lub mniej na końcu)
			fragment_end = min(idx + 11, len(lines_i))
			fragment = lines_i[idx:fragment_end]
			
			# Sprawdź każdy wzorzec z pliku1
			for pattern in patterns:
				if pattern in fragment:
					found_count += 1
					#print(f"\n=== Znaleziono wzorzec '{pattern}' w linii {idx//11 + 1} ===")
					print('\n'.join(fragment))
					#print(f"=== Koniec fragmentu ===\n")
					# Nie przerywamy - szukamy dalszych wzorców w tym fragmencie
					break
		
		print(f"\nZnaleziono łącznie {found_count} dopasowań")
		
	except FileNotFoundError as e:
		print(f"Błąd: Nie znaleziono pliku - {e}")
		return
	except Exception as e:
		print(f"Błąd: {e}")
		return

	stop_time = time.time()
	print(start_msg)
	print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time - start_time))}')
	print('\a', end='', file=sys.stderr)

# https://stackoverflow.com/questions/5925918/python-suppressing-errors-from-going-to-commandline
def supressErrors(*args):
	pass

if __name__ == '__main__':
	sys.tracebacklimit = 0
	sys.stderr = supressErrors()
	
	global start_msg, start_time
	start_msg = ''
	start_time = 0
	
	try:
		main()
	except KeyboardInterrupt:
		print('\nKeyboard break!\a')
		stop_time = time.time()
		
		print(start_msg)
		print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		print(f'Execution took: {str(datetime.timedelta(seconds=stop_time - start_time))}')
		print('\a', end='', file=sys.stderr)
		try:
			sys.exit(130)
		except:
			os._exit(130)
	except Exception as e:
		print(f'Error: {e}')
