#!/usr/bin/env python3

import base58
import datetime
import ecdsa
import hashlib
import secrets
from ecdsa import SigningKey, SECP256k1


# --- Base58 helpers ---
def b58c_to_bytes(s: str) -> bytes:
	return base58.b58decode_check(s)

def bytes_to_b58c(b: bytes) -> str:
	return base58.b58encode_check(b).decode()

def b58c_to_hex(s: str) -> str:
	return base58.b58decode_check(s).hex()

def hex_to_b58c(h: str) -> str:
	return base58.b58encode_check(bytes.fromhex(h)).decode()


# --- Conversion helpers ---
def bytes_to_string(b: bytes) -> str:
	return b.decode("utf-8")

def bytes_to_int(b: bytes) -> int:
	return int.from_bytes(b, "big")

def bytes_to_hex(b: bytes) -> str:
	return b.hex()

def hex_to_bytes(h: str) -> bytes:
	return bytes.fromhex(h)

def hex_to_int(h: str) -> int:
	return int(h, 16)

def hex_to_string(h: str) -> str:
	return bytes.fromhex(h).decode("utf-8")

def int_to_bytes(value: int, length: int | None = None) -> bytes:
	if value == 0 and not length:
		return b"\x00"
	return value.to_bytes(length or (value.bit_length() + 7) // 8, "big")

def int_to_hex(i: int) -> str:
	return format(i, "x")  # czysty hex, bez "0x"

def int_to_str(i: int) -> str:
	return str(i)

def str_to_bytes(s: str) -> bytes:
	return s.encode()

def str_to_hex(s: str) -> str:
	return s.encode().hex()

def reverse_string(s: str) -> str:
	return s[::-1]


# --- Hashing ---
def sha256(b: bytes) -> bytes:
	return hashlib.sha256(b).digest()

def sha256_hex(b: bytes) -> str:
	return hashlib.sha256(b).hexdigest()

def ripemd160(b: bytes) -> bytes:
	return hashlib.new("ripemd160", b).digest()

def ripemd160_hex(b: bytes) -> str:
	return hashlib.new("ripemd160", b).hexdigest()

def hash160(data: bytes) -> bytes:
	return ripemd160(sha256(data))


# --- Bitcoin keys/addresses ---
def pubkey_to_addr(pubkey_hex: str) -> str:
	pubkey_bytes = bytes.fromhex(pubkey_hex)
	vh160 = b"\x00" + hash160(pubkey_bytes)
	checksum = sha256(sha256(vh160))[:4]
	return base58.b58encode(vh160 + checksum).decode()

def pvk_to_pubkey(key: bytes | str) -> str:
	key_bytes = bytes.fromhex(key) if isinstance(key, str) else key
	sk = SigningKey.from_string(key_bytes, curve=SECP256k1)
	return (b"\x04" + sk.verifying_key.to_string()).hex()

def pvk_to_addr(pvk: bytes | str) -> str:
	return pubkey_to_addr(pvk_to_pubkey(pvk))

def pvk_to_wif(key_bytes: bytes) -> str:
	return base58.b58encode_check(b"\x80" + key_bytes).decode()

def wif_to_pvk(wif: str) -> str:
	return base58.b58decode_check(wif)[1:].hex()

def entropy_to_pvk(e: str) -> str | None:
	order = SECP256k1.order
	entropy_int = int(e, 16)
	if not (1 <= entropy_int < order):
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	return private_key.to_string().hex()

def generate_random_private_key() -> str:
	return secrets.token_hex(32)


# --- Utils ---
def count_lines(file: str) -> int:
	with open(file, "r") as f:
		return sum(1 for _ in f)

def substring_after(s, delim):
	return s.partition(delim)[2]

def substring_before(s, delim):
	return s.partition(delim)[0]

def find_all_matches(pattern, string):
	import re
	pat = re.compile(pattern)
	return [m.group(0) for m in pat.finditer(string)]

def log(message: str):
	ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open("log.txt", "a") as f:
		f.write(f"{ts} {message}\n")
	print(f"{ts} {message}", flush=True)


# --- Test run ---
if __name__ == "__main__":
	print(b58c_to_bytes('1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY'))
	print(bytes_to_b58c(b'\x00\xc8%\xa1\xec\xf2\xa6\x83\x0cD\x01b\x0c:\x16\xf1\x99PW\xc2\xab'))
	print(bytes_to_string(b'abc123'))
	print(bytes_to_int(b'\x80\x00'))
	print(bytes_to_hex(b'\x80\x00'))
	print(count_lines(__file__))
	print(hex_to_bytes('8000'))
	print(hex_to_int('8000'))
	print(int_to_bytes(32768))
	print(int_to_str(65))
	print(int_to_hex(32768))
	print(pubkey_to_addr('0430210c23b1a047bc9bdbb13448e67deddc108946de6de639bcc75d47c0216b1be383c4a8ed4fac77c0d2ad737d8499a362f483f8fe39d1e86aaed578a9455dfc'))
	print(pvk_to_wif(bytes.fromhex("000000000000000000000000000000000000000000000001a838b13505b26867")))
	print(wif_to_pvk('5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ipCnYRNeQuRFKarWVVs'))
