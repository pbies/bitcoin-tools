#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Tabs for indentation per user preference.

# Requirements:
#   sudo apt install python3-pip
#   pip3 install hdwallet tqdm web3 bip32utils requests base58 ecdsa mnemonic

import os
import sys
import math
import binascii
import hashlib
import pprint
import requests
import base58
import ecdsa
import mnemonic
import bip32utils
from tqdm import tqdm
from web3 import Web3
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed

# -------- Configuration --------
ALCHEMY_BASE = "https://eth-mainnet.g.alchemy.com/v2/"
REQ_TIMEOUT = 12  # seconds
VERSION = "0.61"
BANNER = f"Tool for cc v{VERSION} (C) 2023-2026 Aftermath @Tzeeck"

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
BASE58_CHARS = set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')

# -------- Utilities --------
def clear():
	os.system('cls' if os.name == 'nt' else 'clear')

def input_default(prompt: str, default: str) -> str:
	val = input(prompt)
	return default if val.strip() == "" else val

def safe_int(s: str) -> int:
	try:
		return int(s)
	except ValueError:
		print("Not an integer!")
		return 0

def hex_zfill(h: str, width: int) -> str:
	h = h.strip().lower().replace("0x", "")
	return h.zfill(width)

def is_hex(s: str) -> bool:
	try:
		int(s, 16)
		return True
	except ValueError:
		return False

# -------- Validation helpers --------
def _nh(s: str) -> str:
	return s.strip().lower().replace('0x', '')

def _is_valid_hex_str(s: str) -> bool:
	h = _nh(s)
	return len(h) > 0 and all(c in '0123456789abcdef' for c in h)

def validate_privkey_hex(s: str) -> tuple[bool, str]:
	h = _nh(s)
	if not h:
		return False, "Empty input."
	if not all(c in '0123456789abcdef' for c in h):
		return False, "Not a valid hex string."
	if len(h) > 64:
		return False, "Too long: max 64 hex chars (32 bytes)."
	val = int(h, 16)
	if val == 0:
		return False, "Private key cannot be zero."
	if val >= SECP256K1_ORDER:
		return False, "Value exceeds secp256k1 curve order."
	return True, ""

def validate_privkey_int(s: str) -> tuple[bool, int, str]:
	try:
		val = int(s.strip())
	except ValueError:
		return False, 0, "Not a valid integer."
	if val <= 0:
		return False, 0, "Must be a positive integer."
	if val >= SECP256K1_ORDER:
		return False, 0, "Value exceeds secp256k1 curve order."
	return True, val, ""

def validate_pubkey_hex(s: str) -> bool:
	h = _nh(s)
	if not all(c in '0123456789abcdef' for c in h):
		return False
	if len(h) == 66:
		return h[:2] in ('02', '03')
	if len(h) == 130:
		return h[:2] == '04'
	return False

def validate_mnemonic_words(words: str) -> bool:
	return len(words.strip().split()) in (12, 15, 18, 21, 24)

def validate_btc_address(s: str) -> bool:
	s = s.strip()
	if not s:
		return False
	if s[0] in ('1', '3'):
		return 25 <= len(s) <= 34
	if len(s) >= 3 and s[:3].lower() == 'bc1':
		return 14 <= len(s) <= 74
	return False

def validate_eth_address(s: str) -> bool:
	s = s.strip()
	if s.lower().startswith('0x'):
		s = s[2:]
	return len(s) == 40 and all(c in '0123456789abcdefABCDEF' for c in s)

def validate_wif(s: str) -> bool:
	s = s.strip()
	return bool(s) and s[0] in ('5', 'K', 'L') and 51 <= len(s) <= 52

def validate_base58_str(s: str) -> bool:
	return bool(s.strip()) and all(c in BASE58_CHARS for c in s.strip())

# -------- Core conversions --------
def bw2wif_single(s: str) -> str:
	sha = hashlib.sha256(s.encode('utf-8')).digest()
	tmp = b'\x80' + sha
	return base58.b58encode_check(tmp).decode('ascii')

def bw2wif_many(infile: str, outfile: str) -> None:
	try:
		with open(infile, 'r', encoding='utf-8', errors='replace') as f:
			total = sum(1 for _ in f)
	except FileNotFoundError:
		print(f"Input file not found: {infile}")
		return

	with open(infile, 'r', encoding='utf-8', errors='replace') as f1, \
		 open(outfile, 'w', encoding='utf-8') as f2:
		for line in tqdm(f1, total=total, unit=" lines"):
			word = line.rstrip("\n")
			sha = hashlib.sha256(word.encode('utf-8')).digest()
			tmp = b'\x80' + sha
			wif = base58.b58encode_check(tmp).decode('ascii')
			f2.write(f"{wif} 0 # {word}\n")

def wif_uncompressed_from_hex(priv_hex: str) -> str:
	priv_hex = hex_zfill(priv_hex, 64)
	payload = b'\x80' + bytes.fromhex(priv_hex)
	return base58.b58encode_check(payload).decode('ascii')

def wif_compressed_from_hex(priv_hex: str) -> str:
	priv_hex = hex_zfill(priv_hex, 64)
	payload = b'\x80' + bytes.fromhex(priv_hex) + b'\x01'
	return base58.b58encode_check(payload).decode('ascii')

def wif_to_privhex(wif: str) -> str:
	raw = base58.b58decode_check(wif)
	if len(raw) not in (33, 34):
		raise ValueError("Unexpected WIF payload length.")
	if raw[0] != 0x80:
		raise ValueError("Not a mainnet WIF (0x80).")
	key = raw[1:]
	if len(key) == 33 and key[-1] == 0x01:
		key = key[:-1]
	return key.hex()

def privhex_to_pubkey_uncompressed(priv_hex: str) -> str:
	priv_hex = hex_zfill(priv_hex, 64)
	sk = ecdsa.SigningKey.from_string(bytes.fromhex(priv_hex), curve=ecdsa.SECP256k1)
	return (b'\x04' + sk.verifying_key.to_string()).hex()

def pubkey_hash160_from_pubhex(pub_hex: str) -> str:
	pub_bytes = bytes.fromhex(pub_hex)
	sha = hashlib.sha256(pub_bytes).digest()
	return hashlib.new("ripemd160", sha).hexdigest()

def address_p2pkh_from_pubhex(pub_hex: str) -> str:
	h160 = bytes.fromhex(pubkey_hash160_from_pubhex(pub_hex))
	payload = b'\x00' + h160
	return base58.b58encode_check(payload).decode('ascii')

def address_from_string(label: str) -> str:
	if len(label) > 20:
		raise ValueError("String too long (max 20).")
	raw = b'\x00' + label.encode('utf-8')
	raw = raw.ljust(1 + 20, b'\x20')
	return base58.b58encode_check(raw).decode('ascii')

def string_from_address(addr: str) -> str:
	data = base58.b58decode_check(addr)
	return data.decode('utf-8', errors='replace')

def base58check_decode_to_hex(s: str) -> str:
	return base58.b58decode_check(s).hex()

def base58check_encode_from_hex(h: str) -> str:
	return base58.b58encode_check(bytes.fromhex(h)).decode('ascii')

def hex_to_bytes_file(hex_str: str, out_path: str = "output.bin") -> None:
	with open(out_path, 'wb') as f:
		f.write(bytes.fromhex(hex_zfill(hex_str, len(hex_str))))

def bytes_file_to_hex(in_path: str = "input.bin") -> str:
	with open(in_path, 'rb') as f:
		return f.read().hex()

def count_lines(path: str) -> int:
	try:
		with open(path, 'r', encoding='utf-8', errors='replace') as f:
			return sum(1 for _ in f)
	except FileNotFoundError:
		print(f"File not found: {path}")
		return 0

def hex_to_int(h: str) -> int:
	return int(h, 16)

def int_to_hex(i: str) -> str:
	return hex(int(i))

def int_to_bytes_be(value: int, length: int = None) -> bytearray:
	if length is None:
		if value == 0:
			return bytearray([0])
		length = 1 + int(math.log(value, 256))
	out = []
	for i in range(length):
		out.append((value >> (8 * (length - 1 - i))) & 0xff)
	return bytearray(out)

def sha256_file_to_file(inp: str, outp: str) -> None:
	with open(inp, 'rb') as f, open(outp, 'wb') as o:
		o.write(hashlib.sha256(f.read()).digest())

def ripemd160_file_to_file(inp: str, outp: str) -> None:
	with open(inp, 'rb') as f, open(outp, 'wb') as o:
		o.write(hashlib.new('ripemd160', f.read()).digest())

def sha256_hex_of_hex(h: str) -> str:
	return hashlib.sha256(bytes.fromhex(h)).hexdigest()

def ripemd160_hex_of_hex(h: str) -> str:
	return hashlib.new('ripemd160', bytes.fromhex(h)).hexdigest()

def hex_to_utf8_string(h: str) -> str:
	return bytes.fromhex(h).decode('utf-8')

# -------- External queries --------
def check_btc_balance(addr: str) -> int:
	try:
		r = requests.get(f'https://blockchain.info/q/addressbalance/{addr}', timeout=REQ_TIMEOUT)
		r.raise_for_status()
		return int(r.text)
	except requests.RequestException as e:
		print(f'Error fetching BTC balance: {e}')
		return -1
	except ValueError:
		print('Error: non-integer response for BTC balance.')
		return -1

def get_pubkey_for_address(addr: str) -> str | None:
	try:
		r = requests.get(f'https://blockchain.info/q/pubkeyaddr/{addr}', timeout=REQ_TIMEOUT)
		if r.status_code == 404:
			print("Not found (no pubkey visible for this address).")
			return None
		r.raise_for_status()
		return r.text.strip()
	except requests.RequestException as e:
		print(f'Error fetching pubkey: {e}')
		return None

def check_eth_balance(addr: str, api_key: str) -> int:
	try:
		w3 = Web3(Web3.HTTPProvider(ALCHEMY_BASE + api_key))
		cksum = Web3.to_checksum_address(addr)
		return w3.eth.get_balance(cksum)
	except Exception as e:
		print(f'Error fetching ETH balance: {e}')
		return -1

# -------- HD / BIP helpers --------
def bip39_to_wif(mnemonic_words: str, n1: int, n2: int) -> str:
	mobj = mnemonic.Mnemonic("english")
	seed = mobj.to_seed(mnemonic_words)
	root = bip32utils.BIP32Key.fromEntropy(seed)
	child = root.ChildKey(n1 + bip32utils.BIP32_HARDEN)\
	            .ChildKey(n2 + bip32utils.BIP32_HARDEN)\
	            .ChildKey(0 + bip32utils.BIP32_HARDEN)\
	            .ChildKey(0).ChildKey(0)
	return child.WalletImportFormat()

def pubkey_to_all_addresses(pk_hex: str) -> None:
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdw.from_public_key(public_key=pk_hex)
	print()
	print(f'P2PKH:          {hdw.address("P2PKH")}')
	print(f'P2SH:           {hdw.address("P2SH")}')
	print(f'P2TR:           {hdw.address("P2TR")}')
	print(f'P2WPKH:         {hdw.address("P2WPKH")}')
	print(f'P2WPKH-In-P2SH: {hdw.address("P2WPKH-In-P2SH")}')
	print(f'P2WSH:          {hdw.address("P2WSH")}')
	print(f'P2WSH-In-P2SH:  {hdw.address("P2WSH-In-P2SH")}')
	print()

# -------- Menu actions --------
def action_seed_phrase_to_hdwallet():
	j = input('Enter seed phrase = mnemonic: ').strip()
	if not j:
		print("Error: empty input.")
		return
	if not validate_mnemonic_words(j):
		print("Error: word count must be 12, 15, 18, 21, or 24.")
		return
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	try:
		hdw.from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=j))
		print()
		pprint.pprint(hdw.dump())
		print()
	except Exception as e:
		print("Error: " + str(e))

def action_seed_hex_to_hdwallet():
	j = input('Enter seed hex: ').strip()
	if not _is_valid_hex_str(j):
		print("Error: not a valid hex string.")
		return
	j = hex_zfill(j, 128)
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	try:
		hdw.from_seed(seed=BIP39Seed(j))
		print()
		pprint.pprint(hdw.dump())
		print()
	except Exception as e:
		print("Error: " + str(e))

def action_mnemonic_to_wif_bch():
	a = input('Enter BCH mnemonic (seed phrase, usually 12 words): ').strip()
	if not a:
		print("Error: empty input.")
		return
	if not validate_mnemonic_words(a):
		print("Error: word count must be 12, 15, 18, 21, or 24.")
		return
	try:
		print('\nWIF: ' + bip39_to_wif(a, 44, 145) + '\n')
	except Exception as e:
		print("Error: " + str(e))

def action_mnemonic_to_wif_btc():
	a = input('Enter BTC mnemonic (seed phrase, usually 12 words): ').strip()
	if not a:
		print("Error: empty input.")
		return
	if not validate_mnemonic_words(a):
		print("Error: word count must be 12, 15, 18, 21, or 24.")
		return
	try:
		print('\nWIF: ' + bip39_to_wif(a, 84, 0) + '\n')
	except Exception as e:
		print("Error: " + str(e))

def action_mnemonic_to_wif_ltc():
	a = input('Enter LTC mnemonic (seed phrase, usually 12 words): ').strip()
	if not a:
		print("Error: empty input.")
		return
	if not validate_mnemonic_words(a):
		print("Error: word count must be 12, 15, 18, 21, or 24.")
		return
	try:
		print('\nWIF: ' + bip39_to_wif(a, 84, 2) + '\n')
	except Exception as e:
		print("Error: " + str(e))

def action_priv_int_to_wif():
	i = input('Enter integer: ').strip()
	ok, val, errmsg = validate_privkey_int(i)
	if not ok:
		print("Error: " + errmsg)
		return
	key_hex = hex(val)[2:].zfill(64)
	print('\nWIF uncomp: ' + wif_uncompressed_from_hex(key_hex))
	print('WIF comp  : ' + wif_compressed_from_hex(key_hex) + '\n')

def action_priv_int_to_hdwallet():
	a = input('Enter integer: ').strip()
	ok, val, errmsg = validate_privkey_int(a)
	if not ok:
		print("Error: " + errmsg)
		return
	b = hex(val)[2:].zfill(64)
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	try:
		hdw.from_private_key(private_key=b)
		print()
		pprint.pprint(hdw.dump())
		print('\nWIF uncomp: ' + wif_uncompressed_from_hex(b) + '\n')
	except Exception as e:
		print("Error: " + str(e))

def action_priv_hex_to_wif():
	a = input('Enter private key in hex: ').strip()
	ok, errmsg = validate_privkey_hex(a)
	if not ok:
		print("Error: " + errmsg)
		return
	a = hex_zfill(a, 64)
	print('\nWIF uncomp: ' + wif_uncompressed_from_hex(a))
	print('WIF comp  : ' + wif_compressed_from_hex(a) + '\n')

def action_priv_hex_to_pubkey():
	a = input('Enter private key in hex: ').strip()
	ok, errmsg = validate_privkey_hex(a)
	if not ok:
		print("Error: " + errmsg)
		return
	a = hex_zfill(a, 64)
	print('\nPublic key: ' + privhex_to_pubkey_uncompressed(a) + '\n')

def action_priv_hex_to_hdwallet():
	j = input('Enter private key hex: ').strip()
	ok, errmsg = validate_privkey_hex(j)
	if not ok:
		print("Error: " + errmsg)
		return
	j = hex_zfill(j, 64)
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	try:
		hdw.from_private_key(private_key=j)
		print()
		pprint.pprint(hdw.dump())
		print('\nWIF uncomp: ' + wif_uncompressed_from_hex(j) + '\n')
	except Exception as e:
		print("Error: " + str(e))

def action_brainwallet_single():
	a = input('Enter brainwallet: ')
	if not a:
		print("Error: empty input.")
		return
	print('\nWIF: ' + bw2wif_single(a) + '\n')

def action_brainwallet_many():
	a = input_default('Enter input filename [input.txt]: ', 'input.txt')
	if not os.path.isfile(a):
		print("Error: input file not found: " + a)
		return
	b = input_default('Enter output filename [output.txt]: ', 'output.txt')
	bw2wif_many(a, b)
	print('Done!\n')

def action_pubkey_to_addresses():
	a = input('Enter public key (hex): ').strip()
	if not validate_pubkey_hex(a):
		print("Error: must be compressed (66 hex, 02/03 prefix) or uncompressed (130 hex, 04 prefix).")
		return
	pubkey_to_all_addresses(a)

def action_pubkey_hex_to_hash160():
	h = input('Enter public key (hex): ').strip()
	if not validate_pubkey_hex(h):
		print("Error: must be compressed (66 hex, 02/03 prefix) or uncompressed (130 hex, 04 prefix).")
		return
	print('\nHASH160: ' + pubkey_hash160_from_pubhex(h) + '\n')

def action_address_to_string():
	s = input('Enter address: ').strip()
	if not s:
		print("Error: empty input.")
		return
	try:
		print('\nString: ' + string_from_address(s))
	except Exception as e:
		print(f'Error: {e}')
	print()

def action_address_to_pubkey():
	a = input('Enter BTC address: ').strip()
	if not validate_btc_address(a):
		print("Error: invalid BTC address (must start with 1/3/bc1, valid length).")
		return
	res = get_pubkey_for_address(a)
	if res:
		print('\nPublic key:\n' + res + '\n')

def action_hex_to_string():
	a = input('Enter hex: ').strip()
	if not _is_valid_hex_str(a):
		print("Error: not a valid hex string.")
		return
	try:
		print('\nString: ' + hex_to_utf8_string(a) + '\n')
	except Exception:
		print("\nNot UTF-8 printable bytes, cannot convert!\n")

def action_string_to_hex():
	a = input('Enter string: ')
	if not a:
		print("Error: empty input.")
		return
	print('\nHex: ' + binascii.hexlify(a.encode('utf-8')).decode('ascii') + '\n')

def action_string_to_address():
	h = input('Enter string (up to 20 chars): ')
	if not h:
		print("Error: empty input.")
		return
	try:
		addr = address_from_string(h)
		print('\nAddress: ' + addr + '\n')
	except ValueError as e:
		print("Error: " + str(e))

def action_hex_to_int():
	a = input('Enter hex: ').strip()
	if not _is_valid_hex_str(a):
		print("Error: not a valid hex string.")
		return
	print('\nInteger: ' + str(hex_to_int(a)) + '\n')

def action_int_to_hex():
	a = input('Enter int: ').strip()
	try:
		int(a)
	except ValueError:
		print("Error: not a valid integer.")
		return
	print('\nHex: ' + int_to_hex(a) + '\n')

def action_b58_decode():
	a = input('Enter Base58Check encoded string: ').strip()
	if not a:
		print("Error: empty input.")
		return
	if not validate_base58_str(a):
		print("Error: invalid Base58 characters in input.")
		return
	try:
		print('\n' + base58check_decode_to_hex(a) + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_b58_encode():
	a = input('Enter hex string: ').strip()
	if not _is_valid_hex_str(a):
		print("Error: not a valid hex string.")
		return
	try:
		print('\n' + base58check_encode_from_hex(a) + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_bytes_file_to_hex():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	if not os.path.isfile(a):
		print("Error: file not found: " + a)
		return
	try:
		print('\nHex: ' + bytes_file_to_hex(a) + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_hex_to_bytes_file():
	a = input('Enter hex string: ').strip()
	if not _is_valid_hex_str(a):
		print("Error: not a valid hex string.")
		return
	hex_to_bytes_file(a, 'output.bin')
	print('\nWritten to output.bin\n')

def action_count_lines():
	a = input_default('Enter filename [input.txt]: ', 'input.txt')
	if not os.path.isfile(a):
		print("Error: file not found: " + a)
		return
	print('\nLines count: ' + str(count_lines(a)) + '\n')

def action_sha256_binary():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	if not os.path.isfile(a):
		print("Error: input file not found: " + a)
		return
	b = input_default('Enter output filename [output.bin]: ', 'output.bin')
	sha256_file_to_file(a, b)
	print("Done.\n")

def action_sha256_hex_file():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	if not os.path.isfile(a):
		print("Error: file not found: " + a)
		return
	try:
		with open(a, 'rb') as f:
			print('\nSHA256: ' + hashlib.sha256(f.read()).hexdigest() + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_ripemd160_binary():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	if not os.path.isfile(a):
		print("Error: input file not found: " + a)
		return
	b = input_default('Enter output filename [output.bin]: ', 'output.bin')
	ripemd160_file_to_file(a, b)
	print("Done.\n")

def action_ripemd160_hex_file():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	if not os.path.isfile(a):
		print("Error: file not found: " + a)
		return
	try:
		with open(a, 'rb') as f:
			print('\nRIPEMD160: ' + hashlib.new('ripemd160', f.read()).hexdigest() + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_sha256_of_hex():
	h = input('Enter hex: ').strip()
	if not _is_valid_hex_str(h):
		print("Error: not a valid hex string.")
		return
	print('\nSHA256: ' + sha256_hex_of_hex(h) + '\n')

def action_ripemd160_of_hex():
	h = input('Enter hex: ').strip()
	if not _is_valid_hex_str(h):
		print("Error: not a valid hex string.")
		return
	print('\nRIPEMD160: ' + ripemd160_hex_of_hex(h) + '\n')

def action_generate_set():
	pvk = os.urandom(32)
	pvkhex = pvk.hex().zfill(64)
	print('\nPrivate key: ' + pvkhex)
	wif1 = wif_uncompressed_from_hex(pvkhex)
	wif2 = wif_compressed_from_hex(pvkhex)
	print('WIF uncomp : ' + wif1)
	print('WIF comp   : ' + wif2)
	pub_uncomp = privhex_to_pubkey_uncompressed(pvkhex)
	print('Public key : ' + pub_uncomp)
	pubkey_to_all_addresses(pub_uncomp)

def action_generate_hd_wallet():
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdw.from_seed(seed=BIP39Seed(seed=os.urandom(64).hex()))
	pp = pprint.PrettyPrinter(indent=4)
	print('\n' + pp.pformat(hdw.dump()) + '\n')

def action_check_btc_balance():
	a = input('Enter BTC address: ').strip()
	if not validate_btc_address(a):
		print("Error: invalid BTC address (must start with 1/3/bc1, valid length).")
		return
	sat = check_btc_balance(a)
	if sat >= 0:
		print('\n' + a + '\t' + str(sat) + ' sat\t' + str(sat / 100000) + ' mBTC\t' + str(sat / 100000000) + ' BTC\n')

def action_check_eth_balance():
	a = input('Enter ETH address: ').strip()
	if not validate_eth_address(a):
		print("Error: invalid ETH address (expected 0x + 40 hex chars).")
		return
	k = input('Enter Alchemy API key: ').strip()
	if not k:
		print("Error: API key cannot be empty.")
		return
	sat = check_eth_balance(a, k)
	if sat >= 0:
		print('\n' + a + ' = ' + str(sat / 1e18) + ' ETH\n')

def action_wif_to_privkey_hex():
	w = input('Enter WIF: ').strip()
	if not w:
		print("Error: empty input.")
		return
	if not validate_wif(w):
		print("Error: invalid WIF (must start with 5/K/L, length 51-52).")
		return
	try:
		p = wif_to_privhex(w)
		print('\nPrivate key: ' + p + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_eth_mnemonic_to_address():
	k = input('Enter Alchemy API key: ').strip()
	if not k:
		print("Error: API key cannot be empty.")
		return
	j = input('Enter seed phrase = mnemonic: ').strip()
	if not j:
		print("Error: empty input.")
		return
	if not validate_mnemonic_words(j):
		print("Error: word count must be 12, 15, 18, 21, or 24.")
		return
	w3 = Web3(Web3.HTTPProvider(ALCHEMY_BASE + k))
	w3.eth.account.enable_unaudited_hdwallet_features()
	try:
		acc = w3.eth.account.from_mnemonic(j)
		address = w3.to_checksum_address(acc.address)
		h = acc._private_key.hex()
		print()
		print('Checksum address: ' + address)
		print('Private key: ' + h)
		print()
	except Exception:
		print('Error: bad mnemonic', file=sys.stderr)

# -------- Main loop --------
MENU = """
{banner}
Mostly all options are for BTC if not mentioned differently

1. seed phrase = mnemonic to HDWallet
2. seed hex to HDWallet
3. mnemonic to WIF - BCH Bitcoin Cash
4. mnemonic to WIF - BTC Bitcoin
5. mnemonic to WIF - LTC Litecoin
6. private key integer to WIF
7. private key integer to HDWallet
8. private key hex to WIF
9. private key hex to public key
a. private key hex to HDWallet
b. brainwallet to WIF - single
c. brainwallet to WIF - many (a file)
d. public key to address
e. public key hex to hash160
f. address to string
g. address to public key
h. hex to string
i. string to hex
j. string to address
k. hex to int
l. int to hex
m. decode Base58Check to hex
n. encode hex to Base58Check
o. generate set
p. generate HD wallet
q. check BTC balance - single
r. check ETH balance - single
s. WIF to private key hex
t. bytes (file) to hex
u. convert hex to bytes (to file)
v. count lines in file
w. binary SHA256 (files)
x. hex SHA256 (a file)
y. binary RIPEMD160 (files)
z. hex RIPEMD160 (a file)
A. get SHA256 of hex (hex converted to binary)
B. get RIPEMD160 of hex (hex converted to binary)
C. ETH mnemonic (seed phrase) to address and private key
""".strip()

def main():
	sys.stdout.reconfigure(encoding='utf-8', errors='replace')
	clear()
	while True:
		print(MENU.format(banner=BANNER))
		m = input('Select option or enter empty to quit: ').strip()

		if m == '':
			sys.exit(0)

		try:
			match m:
				case '1': action_seed_phrase_to_hdwallet()
				case '2': action_seed_hex_to_hdwallet()
				case '3': action_mnemonic_to_wif_bch()
				case '4': action_mnemonic_to_wif_btc()
				case '5': action_mnemonic_to_wif_ltc()
				case '6': action_priv_int_to_wif()
				case '7': action_priv_int_to_hdwallet()
				case '8': action_priv_hex_to_wif()
				case '9': action_priv_hex_to_pubkey()
				case 'a': action_priv_hex_to_hdwallet()
				case 'b': action_brainwallet_single()
				case 'c': action_brainwallet_many()
				case 'd': action_pubkey_to_addresses()
				case 'e': action_pubkey_hex_to_hash160()
				case 'f': action_address_to_string()
				case 'g': action_address_to_pubkey()
				case 'h': action_hex_to_string()
				case 'i': action_string_to_hex()
				case 'j': action_string_to_address()
				case 'k': action_hex_to_int()
				case 'l': action_int_to_hex()
				case 'm': action_b58_decode()
				case 'n': action_b58_encode()
				case 'o': action_generate_set()
				case 'p': action_generate_hd_wallet()
				case 'q': action_check_btc_balance()
				case 'r': action_check_eth_balance()
				case 's': action_wif_to_privkey_hex()
				case 't': action_bytes_file_to_hex()
				case 'u': action_hex_to_bytes_file()
				case 'v': action_count_lines()
				case 'w': action_sha256_binary()
				case 'x': action_sha256_hex_file()
				case 'y': action_ripemd160_binary()
				case 'z': action_ripemd160_hex_file()
				case 'A': action_sha256_of_hex()
				case 'B': action_ripemd160_of_hex()
				case 'C': action_eth_mnemonic_to_address()
				case _: print('Unknown option.')
		finally:
			input('Press Enter...')

if __name__ == "__main__":
	main()
