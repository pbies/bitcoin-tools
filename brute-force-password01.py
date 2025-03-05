#!/usr/bin/env python3

import itertools
import string

def brute_force_password(target_password, max_length=6, charset=string.printable):
	"""
	Próbuje odgadnąć hasło metodą brute-force, generując kombinacje znaków.
	
	:param target_password: Hasło do złamania
	:param max_length: Maksymalna długość hasła do przeszukania
	:param charset: Zestaw znaków do wykorzystania w ataku (domyślnie litery i cyfry)
	:return: Odkryte hasło lub None, jeśli nie znaleziono
	"""
	c=0
	cnt=50000
	for length in range(1, max_length + 1):
		for attempt in itertools.product(charset, repeat=length):
			attempt_password = ''.join(attempt)
			if c%cnt==0:
				print(f'{attempt_password}', end='\r')
			c=c+1
			if attempt_password == target_password:
				return attempt_password
	return None

# Przykładowe użycie
target = "a123"
found_password = brute_force_password(target, max_length=6)

if found_password:
	print(f"Hasło złamane: {found_password}")
else:
	print("Nie udało się złamać hasła.")
