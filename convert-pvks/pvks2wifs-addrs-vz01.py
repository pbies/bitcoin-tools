#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import os
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Iterable, List, Optional

import coincurve
from tqdm import tqdm

_B58_ALPHA = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def _sha256(data: bytes) -> bytes:
	return hashlib.sha256(data).digest()


def _ripemd160(data: bytes) -> bytes:
	h = hashlib.new('ripemd160')
	h.update(data)
	return h.digest()


def _hash160(data: bytes) -> bytes:
	return _ripemd160(_sha256(data))


def _dsha256(data: bytes) -> bytes:
	return _sha256(_sha256(data))


def _b58enc(payload: bytes) -> str:
	checksum = _dsha256(payload)[:4]
	data = payload + checksum
	count = 0
	for b in data:
		if b != 0:
			break
		count += 1
	num = int.from_bytes(data, 'big')
	result = []
	while num:
		num, rem = divmod(num, 58)
		result.append(_B58_ALPHA[rem:rem+1])
	result.reverse()
	return (b'1' * count + b''.join(result)).decode('ascii')


def _bech32_encode(hrp: str, witver: int, witprog: bytes) -> str:
	def _convertbits(data, frombits, tobits, pad=True):
		acc = 0; bits = 0; ret = []
		maxv = (1 << tobits) - 1
		for v in data:
			acc = ((acc << frombits) | v) & 0xffffffff
			bits += frombits
			while bits >= tobits:
				bits -= tobits
				ret.append((acc >> bits) & maxv)
		if pad:
			if bits:
				ret.append((acc << (tobits - bits)) & maxv)
		elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
			return None
		return ret

	CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
	data = [witver] + _convertbits(witprog, 8, 5)
	const = 0x2bc830a3 if witver != 0 else 1

	def _polymod(values):
		GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
		chk = 1
		for v in values:
			b = (chk >> 25)
			chk = ((chk & 0x1ffffff) << 5) ^ v
			for i in range(5):
				chk ^= GEN[i] if ((b >> i) & 1) else 0
		return chk

	hrpexp = [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]
	chk = _polymod(hrpexp + data + [0, 0, 0, 0, 0, 0]) ^ const
	checksums = [(chk >> (5 * (5 - i))) & 31 for i in range(6)]
	return hrp + '1' + ''.join(CHARSET[d] for d in data + checksums)


def _wif_uncompressed(privkey: bytes) -> str:
	return _b58enc(b'\x80' + privkey)


def _wif_compressed(privkey: bytes) -> str:
	return _b58enc(b'\x80' + privkey + b'\x01')


def _p2pkh(pubkey: bytes) -> str:
	return _b58enc(b'\x00' + _hash160(pubkey))


def _p2sh_p2wpkh(pubkey_compressed: bytes) -> str:
	h160 = _hash160(pubkey_compressed)
	redeem = b'\x00\x14' + h160
	return _b58enc(b'\x05' + _hash160(redeem))


def _p2wpkh(pubkey_compressed: bytes) -> str:
	return _bech32_encode('bc', 0, _hash160(pubkey_compressed))


def _p2wsh_p2pk(pubkey_compressed: bytes) -> str:
	witness_script = b'\x21' + pubkey_compressed + b'\xac'
	ws_hash = _sha256(witness_script)
	return _bech32_encode('bc', 0, ws_hash)


def _p2wsh_p2wpkh(pubkey_compressed: bytes) -> str:
	witness_script = b'\x21' + pubkey_compressed + b'\xac'
	ws_hash = _sha256(witness_script)
	redeem = b'\x00\x20' + ws_hash
	return _b58enc(b'\x05' + _hash160(redeem))


def _p2tr(pubkey_compressed: bytes) -> str:
	xonly = pubkey_compressed[1:]
	tag = b'TapTweak'
	tag_hash = _sha256(tag)
	tweak_hash = _sha256(tag_hash + tag_hash + xonly)
	tweak_pub = coincurve.PublicKey.from_secret(tweak_hash)
	orig_pub = coincurve.PublicKey(pubkey_compressed)
	tweaked = orig_pub.combine([tweak_pub])
	tweaked_xonly = tweaked.format(compressed=True)[1:]
	return _bech32_encode('bc', 1, tweaked_xonly)


# valid privkey: 1 <= key < N
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def process_raw(raw: bytes) -> Optional[str]:
	if len(raw) != 32:
		return None
	key_int = int.from_bytes(raw, 'big')
	if key_int == 0 or key_int >= _N:
		return None
	try:
		priv = coincurve.PrivateKey(raw)
		pub_c  = priv.public_key.format(compressed=True)
		pub_uc = priv.public_key.format(compressed=False)

		hex_key  = raw.hex()
		wif_u    = _wif_uncompressed(raw)
		wif_c    = _wif_compressed(raw)
		p2pkh_u  = _p2pkh(pub_uc)
		p2pkh_c  = _p2pkh(pub_c)
		p2sh     = _p2sh_p2wpkh(pub_c)
		p2wpkh   = _p2wpkh(pub_c)
		p2wsh    = _p2wsh_p2pk(pub_c)
		p2wsh_sh = _p2wsh_p2wpkh(pub_c)
		p2tr     = _p2tr(pub_c)

		return (
			f"{hex_key}\n"
			f"{wif_u}\n"
			f"{wif_c}\n"
			f"{p2pkh_u}\n"
			f"{p2pkh_c}\n"
			f"{p2sh}\n"
			f"{p2tr}\n"
			f"{p2wpkh}\n"
			f"{p2wsh}\n"
			f"{p2wsh_sh}\n\n"
		)
	except Exception:
		return None


def hex_line_chunks(source, chunk_size: int = 50000) -> Iterable[List[bytes]]:
	"""Read 64-char hex private keys from a file-like object, one per line."""
	chunk: List[bytes] = []
	for line in source:
		line = line.strip()
		if len(line) != 64:
			continue
		try:
			raw = bytes.fromhex(line)
		except ValueError:
			continue
		chunk.append(raw)
		if len(chunk) >= chunk_size:
			yield chunk
			chunk = []
	if chunk:
		yield chunk


def write_results(results, out_path: Path, fsync: bool = False) -> None:
	out_path.parent.mkdir(parents=True, exist_ok=True)
	try:
		with out_path.open('a', encoding='utf-8', buffering=65536) as f:
			wrote = False
			for r in results:
				if r is not None:
					f.write(r)
					wrote = True
			if wrote and fsync:
				f.flush()
				os.fsync(f.fileno())
	except OSError as e:
		print(f"write error: {e}", file=sys.stderr)


def main():
	parser = argparse.ArgumentParser(
		description="Read hex private keys from a file; derive WIFs and addresses."
	)
	parser.add_argument('-i', '--input',   type=str, default='input.txt', help='input file path (default: input.txt)')
	parser.add_argument('-o', '--output',  type=str, default='output.txt', help='output file path')
	parser.add_argument('-w', '--workers', type=int, default=cpu_count()-2,  help='worker processes')
	parser.add_argument('-c', '--chunk',   type=int, default=50000,        help='candidates per chunk')
	parser.add_argument('--fsync',         action='store_true',            help='fsync after each chunk (slow)')
	args = parser.parse_args()

	if not Path(args.input).exists():
		print(f"error: input file not found: {args.input}", file=sys.stderr)
		sys.exit(1)

	out_path = Path(args.output)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text('', encoding='utf-8')

	workers = max(1, min(args.workers, cpu_count()))

	pbar = tqdm(unit=' keys', ncols=132)

	with open(args.input, encoding='utf-8') as f:
		if workers == 1:
			for chunk in hex_line_chunks(f, args.chunk):
				results = [process_raw(raw) for raw in chunk]
				write_results(results, out_path, fsync=args.fsync)
				pbar.update(len(chunk))
		else:
			with Pool(processes=workers) as pool:
				for chunk in hex_line_chunks(f, args.chunk):
					results = list(pool.imap_unordered(process_raw, chunk, chunksize=512))
					write_results(results, out_path, fsync=args.fsync)
					pbar.update(len(chunk))

	pbar.close()
	print('\a', end='', file=sys.stderr)


if __name__ == '__main__':
	main()
