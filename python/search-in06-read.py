#!/usr/bin/env python3

import sys
import os
import datetime
import time
from tqdm import tqdm

class DevNull:
	def write(self, *_):
		pass
	def flush(self):
		pass

def main():
	global start_msg, start_time

	os.system('cls' if os.name == 'nt' else 'clear')
	print(__file__)

	start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time = time.time()

	if len(sys.argv) < 3:
		print("Użycie: python script.py <plik1> <plik2>")
		sys.exit(1)

	try:
		patterns_path = sys.argv[1]
		search_path = sys.argv[2]
		search_size = os.path.getsize(search_path)

		with open(patterns_path, 'r', encoding='utf-8', errors='ignore') as f:
			patterns = {l.rstrip('\n') for l in f if l.rstrip('\n')}

		with open("wyniki.txt", "w", encoding="utf-8") as out, \
		     open(search_path, 'rb') as f_search, \
		     tqdm(
				total=search_size,
				unit='B',
				unit_scale=True,
				desc="szukanie",
				file=sys.stdout,
				leave=True
		     ) as pbar:

			while patterns:
				lines = []
				bytes_read = 0

				for _ in range(11):
					raw = f_search.readline()
					if not raw:
						break
					bytes_read += len(raw)
					lines.append(raw.rstrip(b'\n').decode(errors='ignore'))

				if not lines:
					break

				pbar.update(bytes_read)

				block = set(lines)
				hits = patterns & block

				for h in hits:
					out.write(f"=== Znaleziono '{h}' ===\n")
					out.write('\n'.join(lines) + '\n')
					out.write("=== Koniec fragmentu ===\n\n")
					out.flush()

				patterns -= hits

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

if __name__ == '__main__':
	sys.tracebacklimit = 0
	sys.stderr = DevNull()

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
