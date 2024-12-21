#!/usr/bin/env python3

# Elliptic Curve parameters for secp256k1
MODULUS = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

# Elliptic curve modular arithmetic
def mod_inv(a, p):
	"""Modular inverse using extended Euclidean algorithm."""
	return pow(a, p - 2, p)

def point_add(P, Q):
	"""Add two points on the elliptic curve."""
	if P == (None, None):
		return Q
	if Q == (None, None):
		return P
	x1, y1 = P
	x2, y2 = Q
	if x1 == x2 and y1 != y2:
		return (None, None) # Point at infinity
	if P == Q:
		# Point doubling
		s = (3 * x1 * x1 + A) * mod_inv(2 * y1, MODULUS) % MODULUS
	else:
		# Point addition
		s = (y2 - y1) * mod_inv(x2 - x1, MODULUS) % MODULUS
	x3 = (s * s - x1 - x2) % MODULUS
	y3 = (s * (x1 - x3) - y1) % MODULUS
	return (x3, y3)

def point_mul(k, P):
	"""Multiply a point P by an integer k."""
	R = (None, None) # Point at infinity
	while k:
		if k & 1:
			R = point_add(R, P)
		P = point_add(P, P)
		k >>= 1
	return R

# BSGS algorithm for solving discrete logarithm on elliptic curves
def bsgs(G, P, n):
	"""Baby-Step Giant-Step algorithm for elliptic curve discrete logarithm."""
	import math
	m = math.isqrt(n) + 1
	
	# Baby steps: compute and store G, 2G, 3G, ..., mG
	baby_steps = {}
	for i in range(m):
		baby_steps[point_mul(i, G)] = i
	
	# Giant step: compute -mG
	mG = point_mul(m, G)
	inv_mG = (mG[0], (-mG[1]) % MODULUS)
	
	# Giant steps: walk through P - j * mG and check baby steps
	current = P
	for j in range(m):
		if current in baby_steps:
			return j * m + baby_steps[current]
		current = point_add(current, inv_mG)
	
	raise ValueError("Discrete logarithm not found")

# Example usage
if __name__ == "__main__":
	# Example: Solve for x in x * G = P
	x = 12345 # Private key (for testing)
	Q = point_mul(x, G) # Public key
	
	print("Public key:", Q)
	found_x = bsgs(G, Q, MODULUS)
	print("Recovered private key:", found_x)
	assert found_x == x
