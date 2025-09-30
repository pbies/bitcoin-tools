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
VERSION = "0.60"
BANNER = f"Tool for cc v{VERSION} (C) 2023-2025 Aftermath @Tzeeck"

# -------- Utilities --------
def clear():
	"""Clear terminal screen."""
	os.system('cls' if os.name == 'nt' else 'clear')

def input_default(prompt: str, default: str) -> str:
	"""Prompt with default value when user hits Enter."""
	val = input(prompt)
	return default if val.strip() == "" else val

def safe_int(s: str) -> int:
	try:
		return int(s)
	except ValueError:
		print("Not an integer!")
		return 0

def hex_zfill(h: str, width: int) -> str:
	"""Left-pad hex string (no 0x) to width."""
	h = h.strip().lower().replace("0x", "")
	return h.zfill(width)

def is_hex(s: str) -> bool:
	try:
		int(s, 16)
		return True
	except ValueError:
		return False

# -------- Core conversions --------
def bw2wif_single(s: str) -> str:
	sha = hashlib.sha256(s.encode('utf-8')).digest()
	tmp = b'\x80' + sha  # 0x80 + 32 bytes
	return base58.b58encode_check(tmp).decode('ascii')

def bw2wif_many(infile: str, outfile: str) -> None:
	# Count lines first for tqdm total
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
	# Handles both compressed and uncompressed: drop 0x80 prefix and optional 0x01 suffix
	raw = base58.b58decode_check(wif)
	if len(raw) not in (33, 34):  # 0x80 + 32 or 0x80 + 32 + 0x01
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
	# HASH160(pubkey) = RIPEMD160(SHA256(pubkey_bytes))
	pub_bytes = bytes.fromhex(pub_hex)
	sha = hashlib.sha256(pub_bytes).digest()
	return hashlib.new("ripemd160", sha).hexdigest()

def address_p2pkh_from_pubhex(pub_hex: str) -> str:
	h160 = bytes.fromhex(pubkey_hash160_from_pubhex(pub_hex))
	payload = b'\x00' + h160  # mainnet P2PKH version
	return base58.b58encode_check(payload).decode('ascii')

def address_from_string(label: str) -> str:
	# Construct Base58Check with version 0x00 and ASCII (padded to 20) – as in original script
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
	j = input('Enter seed phrase = mnemonic: ')
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdw.from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=j))
	d = hdw.dump()
	print()
	pprint.pprint(d)
	print()

def action_seed_hex_to_hdwallet():
	j = input('Enter seed hex: ')
	j = hex_zfill(j, 128)
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdw.from_seed(seed=BIP39Seed(j))
	print()
	pprint.pprint(hdw.dump())
	print()

def action_mnemonic_to_wif_bch():
	a = input('Enter BCH mnemonic (seed phrase, usually 12 words): ')
	print('\nWIF: ' + bip39_to_wif(a, 44, 145) + '\n')

def action_mnemonic_to_wif_btc():
	a = input('Enter BTC mnemonic (seed phrase, usually 12 words): ')
	print('\nWIF: ' + bip39_to_wif(a, 84, 0) + '\n')

def action_mnemonic_to_wif_ltc():
	a = input('Enter LTC mnemonic (seed phrase, usually 12 words): ')
	print('\nWIF: ' + bip39_to_wif(a, 84, 2) + '\n')

def action_priv_int_to_wif():
	i = input('Enter integer: ')
	try:
		val = int(i)
	except ValueError:
		print('Not an integer.')
		return
	key_hex = hex(val)[2:].zfill(64)
	print('\nWIF uncomp: ' + wif_uncompressed_from_hex(key_hex))
	print('WIF comp  : ' + wif_compressed_from_hex(key_hex) + '\n')

def action_priv_int_to_hdwallet():
	a = input('Enter integer: ')
	b = hex(int(a))[2:].zfill(64)
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdw.from_private_key(private_key=b)
	print()
	pprint.pprint(hdw.dump())
	print('\nWIF uncomp: ' + wif_uncompressed_from_hex(b) + '\n')

def action_priv_hex_to_wif():
	a = input('Enter private key in hex: ')
	a = hex_zfill(a, 64)
	print('\nWIF uncomp: ' + wif_uncompressed_from_hex(a))
	print('WIF comp  : ' + wif_compressed_from_hex(a) + '\n')

def action_priv_hex_to_pubkey():
	a = input('Enter private key in hex: ')
	a = hex_zfill(a, 64)
	print('\nPublic key: ' + privhex_to_pubkey_uncompressed(a) + '\n')

def action_priv_hex_to_hdwallet():
	j = input('Enter private key hex: ')
	j = hex_zfill(j, 64)
	hdw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	hdw.from_private_key(private_key=j)
	print()
	pprint.pprint(hdw.dump())
	print('\nWIF uncomp: ' + wif_uncompressed_from_hex(j) + '\n')

def action_brainwallet_single():
	a = input('Enter brainwallet: ')
	print('\nWIF: ' + bw2wif_single(a) + '\n')

def action_brainwallet_many():
	a = input_default('Enter input filename [input.txt]: ', 'input.txt')
	b = input_default('Enter output filename [output.txt]: ', 'output.txt')
	bw2wif_many(a, b)
	print('Done!\n')

def action_pubkey_to_addresses():
	a = input('Enter public key (hex): ')
	if not is_hex(a):
		print("Not a hex string.")
		return
	pubkey_to_all_addresses(a)

def action_pubkey_hex_to_hash160():
	h = input('Enter public key (hex): ')
	if not is_hex(h):
		print("Not a hex string.")
		return
	print('\nHASH160: ' + pubkey_hash160_from_pubhex(h))
	print()

def action_address_to_string():
	s = input('Enter address: ')
	try:
		print('\nString: ' + string_from_address(s))
	except Exception as e:
		print(f'Error: {e}')
	print()

def action_address_to_pubkey():
	a = input('Enter address: ')
	res = get_pubkey_for_address(a)
	if res:
		print('\nPublic key:\n' + res + '\n')

def action_hex_to_string():
	a = input('Enter hex: ')
	try:
		print('\nString: ' + hex_to_utf8_string(a) + '\n')
	except Exception:
		print("\nNot UTF-8 printable bytes, can't convert!\n")

def action_string_to_hex():
	a = input('Enter string: ')
	print('\nHex: ' + binascii.hexlify(a.encode('utf-8')).decode('ascii') + '\n')

def action_string_to_address():
	h = input('Enter string (up to 20 chars): ')
	try:
		addr = address_from_string(h)
		print('\nAddress: ' + addr + '\n')
	except ValueError as e:
		print(e)

def action_hex_to_int():
	a = input('Enter hex: ')
	print('\nInteger: ' + str(hex_to_int(a)) + '\n')

def action_int_to_hex():
	a = input('Enter int: ')
	print('\nHex: ' + int_to_hex(a) + '\n')

def action_b58_decode():
	a = input('Enter Base58Check encoded string: ')
	try:
		print('\n' + base58check_decode_to_hex(a) + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_b58_encode():
	a = input('Enter hex string: ')
	try:
		print('\n' + base58check_encode_from_hex(a) + '\n')
	except Exception as e:
		print(f'Error: {e}')

def action_bytes_file_to_hex():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	try:
		print('\nHex: ' + bytes_file_to_hex(a) + '\n')
	except FileNotFoundError:
		print(f'File not found: {a}')

def action_hex_to_bytes_file():
	a = input('Enter hex string: ')
	hex_to_bytes_file(a, 'output.bin')
	print('\nWritten to output.bin file\n')

def action_count_lines():
	a = input_default('Enter filename [input.txt]: ', 'input.txt')
	print('\nLines count: ' + str(count_lines(a)) + '\n')

def action_sha256_binary():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	b = input_default('Enter output filename [output.bin]: ', 'output.bin')
	sha256_file_to_file(a, b)

def action_sha256_hex_file():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	try:
		with open(a, 'rb') as f:
			print('\nSHA256: ' + hashlib.sha256(f.read()).hexdigest() + '\n')
	except FileNotFoundError:
		print(f'File not found: {a}')

def action_ripemd160_binary():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	b = input_default('Enter output filename [output.bin]: ', 'output.bin')
	ripemd160_file_to_file(a, b)

def action_ripemd160_hex_file():
	a = input_default('Enter input filename [input.bin]: ', 'input.bin')
	try:
		with open(a, 'rb') as f:
			print('\nRIPEMD160: ' + hashlib.new('ripemd160', f.read()).hexdigest() + '\n')
	except FileNotFoundError:
		print(f'File not found: {a}')

def action_sha256_of_hex():
	h = input('Enter hex: ')
	print('\nSHA256: ' + sha256_hex_of_hex(h) + '\n')

def action_ripemd160_of_hex():
	h = input('Enter hex: ')
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
	a = input('Enter BTC address: ')
	sat = check_btc_balance(a)
	if sat >= 0:
		print('\n', a, '\t', sat, 'sat\t', sat/100000, 'mBTC\t', sat/100000000, 'BTC\n')

def action_check_eth_balance():
	a = input('Enter ETH address: ')
	k = input('Enter Alchemy API key: ')
	sat = check_eth_balance(a, k)
	if sat >= 0:
		print('\n', a, ' = ', sat/1e18, ' ETH\n')

def action_wif_to_privkey_hex():
	w = input('Enter WIF: ')
	try:
		p = wif_to_privhex(w)
		print('\nPrivate key: ' + p + '\n')
	except Exception as e:
		print(f'Error: {e}')

# -------- Main loop --------
MENU = """
{banner}
Mostly all options are for BTC if not mentioned differently

1. seed phrase = mnemonic to HDWallet
5. seed hex to HDWallet
2. mnemonic to WIF - BCH Bitcoin Cash
3. mnemonic to WIF - BTC Bitcoin
4. mnemonic to WIF - LTC Litecoin
6. private key integer to WIF
7. private key integer to HDWallet
8. private key hex to WIF
9. private key hex to public key
a. private key hex to HDWallet
b. brainwallet to WIF - single
c. brainwallet to WIF - many (a file)
d. public key to address
h. public key hex to hash160
g. address to string
i. address to public key
s. hex to string
r. string to hex
f. string to address
t. hex to int
u. int to hex
n. decode Base58Check to hex
o. encode hex to Base58Check
j. generate set
k. generate HD wallet
l. check BTC balance - single
m. check ETH balance - single
e. WIF to private key hex
p. bytes (file) to hex
q. convert hex to bytes (to file)
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
	clear()
	while True:
		print(MENU.format(banner=BANNER))
		m = input('Select option or enter empty to quit: ').strip()

		if m == '':
			sys.exit(0)

		try:
			match m:
				case '1': action_seed_phrase_to_hdwallet()
				case '5': action_seed_hex_to_hdwallet()
				case '2': action_mnemonic_to_wif_bch()
				case '3': action_mnemonic_to_wif_btc()
				case '4': action_mnemonic_to_wif_ltc()
				case '6': action_priv_int_to_wif()
				case '7': action_priv_int_to_hdwallet()
				case '8': action_priv_hex_to_wif()
				case '9': action_priv_hex_to_pubkey()
				case 'a': action_priv_hex_to_hdwallet()
				case 'b': action_brainwallet_single()
				case 'c': action_brainwallet_many()
				case 'd': action_pubkey_to_addresses()
				case 'h': action_pubkey_hex_to_hash160()
				case 'g': action_address_to_string()
				case 'i': action_address_to_pubkey()
				case 's': action_hex_to_string()
				case 'r': action_string_to_hex()
				case 'f': action_string_to_address()
				case 't': action_hex_to_int()
				case 'u': action_int_to_hex()
				case 'n': action_b58_decode()
				case 'o': action_b58_encode()
				case 'j': action_generate_set()
				case 'k': action_generate_hd_wallet()
				case 'l': action_check_btc_balance()
				case 'm': action_check_eth_balance()
				case 'e': action_wif_to_privkey_hex()
				case 'p': action_bytes_file_to_hex()
				case 'q': action_hex_to_bytes_file()
				case 'v': action_count_lines()
				case 'w': action_sha256_binary()
				case 'x': action_sha256_hex_file()
				case 'y': action_ripemd160_binary()
				case 'z': action_ripemd160_hex_file()
				case 'A': action_sha256_of_hex()
				case 'B': action_ripemd160_of_hex()
				case 'C':
					k = input('Enter Alchemy API key: ')
					j = input('Enter seed phrase = mnemonic: ')
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
				case _:
					print('Unknown option.')
		finally:
			input('Press Enter...')

if __name__ == "__main__":
	main()
