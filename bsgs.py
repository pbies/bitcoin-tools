#!/usr/bin/env python3

import math

def bsgs(g, h, p):
	"""
	Baby-step Giant-step algorithm to solve for x in g^x = h (mod p)

	:param g: base g
	:param h: value h
	:param p: prime modulus p
	:return: integer x such that g^x ≡ h (mod p)
	"""
	
	n = math.isqrt(p) + 1 # Calculate the ceiling of square root of p

	# Baby step: Create a hash table (dictionary) for g^j mod p
	value_table = {}
	for j in range(n):
		value = pow(g, j, p)
		value_table[value] = j

	# Giant step: Compute g^(-n) mod p
	g_inv = pow(g, p - 2, p) # Fermat's Little Theorem to compute modular inverse
	g_inv_n = pow(g_inv, n, p)

	# Start looking for the solution
	for i in range(n):
		y = (h * pow(g_inv_n, i, p)) % p
		if y in value_table:
			return i * n + value_table[y]

	return None # No solution found

# Example usage:
g = 2
h = 22
p = 29

x = bsgs(g, h, p)
if x is not None:
	print(f"The discrete logarithm of {h} to the base {g} modulo {p} is {x}.")
else:
	print("No solution found.")
