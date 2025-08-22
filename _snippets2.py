#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import base58
import binascii
import hashlib
import os
from typing import Iterable, List

import ecdsa
from ecdsa import SECP256k1
from bech32 import bech32_encode, convertbits


DEFAULT_BECH32_HRP = "cro"
# Zostawiam ścieżkę BIP44, choć nie jest używana w tym module:
path = "m/44'/0'/0'/0/0"


def privkey_to_pubkey(privkey: bytes) -> bytes:
	"""
	Zwraca klucz publiczny w formacie skompresowanym (33 bajty) dla krzywej secp256k1.
	"""
	if not isinstance(privkey, (bytes, bytearray)) or len(privkey) != 32:
		raise ValueError("privkey musi być dokładnie 32 bajtami")
	sk = ecdsa.SigningKey.from_string(privkey, curve=SECP256k1)
	vk = sk.get_verifying_key()
	return vk.to_string("compressed")


def pubkey_to_address(pubkey: bytes, *, hrp: str = DEFAULT_BECH32_HRP) -> str:
	"""
	Cosmos-like adres Bech32: bech32(hrp, convertbits(RIPEMD160(SHA256(pubkey)), 8->5)).
	"""
	if not isinstance(pubkey, (bytes, bytearray)):
		raise TypeError("pubkey musi być typu bytes")
	sha = hashlib.sha256(pubkey).digest()
	r160 = hashlib.new("ripemd160", sha).digest()  # 20 bajtów
	# Konwersja 8-bit -> 5-bit; pad=True aby uniknąć None
	five_bit = convertbits(r160, 8, 5, True)
	if five_bit is None:
		raise ValueError("convertbits nie powiodło się (wejście niepoprawne)")
	return bech32_encode(hrp, five_bit)


def privkey_to_address(privkey: bytes, *, hrp: str = DEFAULT_BECH32_HRP) -> str:
	"""
	Skrót: privkey -> pubkey (compressed) -> Bech32 address.
	"""
	return pubkey_to_address(privkey_to_pubkey(privkey), hrp=hrp)


def pvk_to_wif(z: bytes | str, *, compressed: bool = True) -> str:
	"""
	Zwraca WIF (Bitcoin mainnet) dla 32-bajtowego klucza prywatnego.
	- z: bytes (32) albo hex string (64 znaki)
	- compressed=True doda sufiks 0x01 przed obliczeniem checksumy
	"""
	if isinstance(z, str):
		try:
			key = bytes.fromhex(z)
		except ValueError as e:
			raise ValueError("z nie jest poprawnym hexem") from e
	else:
		key = bytes(z)

	if len(key) != 32:
		raise ValueError("klucz prywatny musi mieć 32 bajty")

	prefix_payload = b"\x80" + key + (b"\x01" if compressed else b"")
	# Używamy wbudowanego check-encode, zamiast ręcznie liczyć podwójne SHA256.
	return base58.b58encode_check(prefix_payload).decode("ascii")


def lines(path_like: str) -> int:
	"""
	Liczy linie w pliku bez wczytywania całości do pamięci.
	"""
	with open(path_like, "r", encoding="utf-8", errors="replace") as f:
		return sum(1 for _ in f)


def st(path_or_iterable: str | Iterable[str]) -> List[str]:
	"""
	Zwraca listę linii przyciętych z białych znaków.
	- Jeśli podasz ścieżkę (str), czyta z pliku.
	- Jeśli podasz iterowalne linii, przetwarza je wprost.
	"""
	if isinstance(path_or_iterable, str):
		with open(path_or_iterable, "r", encoding="utf-8", errors="replace") as f:
			return [line.strip() for line in f]
	else:
		return [line.strip() for line in path_or_iterable]


if __name__ == "__main__":
	# Krótkie sanity-checki (nie są to testy jednostkowe)
	ex_priv = bytes.fromhex("11" * 32)
	pub = privkey_to_pubkey(ex_priv)
	print("pub(compressed):", pub.hex())
	print("addr(bech32):", pubkey_to_address(pub, hrp=DEFAULT_BECH32_HRP))
	print("wif(compressed):", pvk_to_wif(ex_priv, compressed=True))
