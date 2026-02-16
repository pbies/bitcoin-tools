#!/usr/bin/env python3

import sys
import os
import datetime
import time

def main():
	# Zadeklarowanie zmiennych globalnych wewnątrz funkcji
	global start_msg, start_time
	
	os.system('cls' if os.name == 'nt' else 'clear')
	print(__file__)
	
	start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time = time.time()

	# Sprawdzenie liczby argumentów
	if len(sys.argv) < 3:
		print("Użycie: python script.py <plik1> <plik2>")
		sys.exit(1)

	# Używanie with do automatycznego zamykania plików
	try:
		# Najpierw czytamy cały plik2 do listy
		with open(sys.argv[2], 'r') as i:
			lines_i = [line.rstrip('\n') for line in i.readlines()]
		
		c = len(lines_i)
		
		with open(sys.argv[1], 'r') as f:
			idx = 0
			while idx < c:
				# Pobieramy maksymalnie 11 linii z pliku2
				d = []
				for j in range(0, 11):
					if idx + j < c:
						d.append(lines_i[idx + j])
					else:
						break
				
				# Czytamy linię z pliku1
				l = f.readline()
				if not l:  # Koniec pliku
					break
				l = l.rstrip('\n')
				
				# Sprawdzamy czy linia jest w fragmencie pliku2
				if l in d:
					print('\n'.join(d))
				
				# Przesuwamy się o 11 linii w pliku2
				idx += 11
				
				# Jeśli to ostatni fragment, kończymy
				if idx >= c:
					break
					
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
	
	# Użycie globalnych zmiennych
	global start_msg, start_time
	# Zainicjowanie zmiennych globalnych
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
