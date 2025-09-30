#!/usr/bin/env python3

from os import system, name
from subprocess import check_output
from tqdm import tqdm
from web3 import Web3
import base58
import binascii
import bip32utils
import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import math
import mnemonic
import random
import re
import requests
import struct
import unittest

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/"

def clear():
	if name == 'nt':
		_ = system('cls')
	else:
		_ = system('clear')
	return

def bw2wif1(s):
	sha=hashlib.sha256(s.encode()).digest()
	tmp=b'\x80'+sha
	return base58.b58encode_check(tmp).decode()

def bw2wifmany(i,o):
	f1=open(i,'r')
	f2=open(o,'w')
	cnt=sum(1 for line in open(i))
	for line in tqdm(f1, total=cnt, unit=" lines"):
		x=line.rstrip('\n').encode()
		sha=hashlib.sha256(x).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		i=h+b" 0 # "+x+b'\n'
		f2.write(i.decode())
	return

def checkBTCbal(a):
	r=requests.get('https://blockchain.info/q/addressbalance/'+a)
	if not r.status_code==200:
		print('Error',r.status_code)
		exit(1)
	b=int(r.text)
	return b

def checkETHbal(a,k):
	w3 = Web3(Web3.HTTPProvider(alchemy_url+k))
	cksum=Web3.to_checksum_address(a)
	bal=w3.eth.get_balance(cksum)
	return bal

def bip39(mnemonic_words,n1,n2):
	mobj = mnemonic.Mnemonic("english")
	seed = mobj.to_seed(mnemonic_words)
	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
	bip32_child_key_obj = bip32_root_key_obj.ChildKey(
		n1 + bip32utils.BIP32_HARDEN
	).ChildKey(
		n2 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(0).ChildKey(0)
	return bip32_child_key_obj.WalletImportFormat()

def b58dec(s):
	return base58.b58decode_check(s).hex()

def b58enc(h):
	return base58.b58encode_check(bytes.fromhex(h)).decode()

def hex_to_bytes(hex):
	return bytes.fromhex(hex)

def count_lines(file):
	return sum(1 for line in open(file, 'r'))

def hex_to_int(hex):
	return int(hex, 16)

def int_to_hex(i):
	return hex(int(i))

def pubkey_to_addr(pk):
	if (ord(bytearray.fromhex(pk[-2:])) % 2 == 0):
		public_key_compressed = '02'
	else:
		public_key_compressed = '03'
	public_key_compressed += pk[2:66]
	hex_str = bytearray.fromhex(public_key_compressed)
	sha = hashlib.sha256()
	sha.update(hex_str)
	rip = hashlib.new('ripemd160')
	rip.update(sha.digest())
	key_hash = rip.hexdigest()
	modified_key_hash = '00' + key_hash
	sha = hashlib.sha256()
	hex_str = bytearray.fromhex(modified_key_hash)
	sha.update(hex_str)
	sha_2 = hashlib.sha256()
	sha_2.update(sha.digest())
	checksum = sha_2.hexdigest()[:8]
	byte_25_address = modified_key_hash + checksum
	return base58.b58encode(bytes(bytearray.fromhex(byte_25_address))).decode('utf-8')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def pvk_to_pubkey(h):
	sk = ecdsa.SigningKey.from_string(h, curve=ecdsa.SECP256k1)
	vk = sk.verifying_key
	return (b'\04' + sk.verifying_key.to_string()).hex()

def str_to_hex(text):
	return binascii.hexlify(text.encode()).decode()

def wif_to_pvk(s):
	return base58.b58decode_check(s).hex()

clear()
while True:
	print('Tool for cc v0.21 (C) 2023 Aftermath @Tzeeck')
	print('1. convert brainwallet to WIF - single')
	print('2. convert brainwallet to WIF - many (a file)')
	print('3. check BTC balance - single')
	print('4. check ETH balance - single')
	print('5. mnemonic to WIF - BCH')
	print('6. mnemonic to WIF - BTC')
	print('7. mnemonic to WIF - LTC')
	print('8. decode Base58Check to hex')
	print('9. encode hex to Base58Check')
	print('a. convert hex to bytes (to file)')
	print('b. count lines in file')
	print('c. hex to int')
	print('d. int to hex')
	print('e. public key to address')
	print('f. private key hex to WIF')
	print('g. private key to public key')
	print('h. string to hex')
	print('i. WIF to private key')
	m=input('Enter number or empty to quit: ')

	match m:
		case '1':
			a=input('Enter brainwallet: ')
			print('\nWIF: '+bw2wif1(a)+'\n')
		case '2':
			a=input('Enter input filename [input.txt]: ')
			b=input('Enter output filename [output.txt]: ')
			if a=='':
				a='input.txt'
			if b=='':
				b='output.txt'
			bw2wifmany(a,b)
			print('Done!\n')
		case '3':
			a=input('Enter BTC address: ')
			sat=checkBTCbal(a)
			print('\n',a,'\t',sat,'sat\t',sat/100000,'mBTC\t',sat/100000000,'BTC\n')
		case '4':
			a=input('Enter ETH address: ')
			k=input('Enter Alchemy API key: ')
			sat=checkETHbal(a,k)
			print('\n',a,' = ',sat/1e18,' ETH\n')
		case '5':
			a=input('Enter BCH mnemonic (seed phrase, usually 12 words): ')
			print('\nWIF: '+bip39(a,44,145)+'\n')
		case '6':
			a=input('Enter BTC mnemonic (seed phrase, usually 12 words): ')
			print('\nWIF: '+bip39(a,84,0)+'\n')
		case '7':
			a=input('Enter LTC mnemonic (seed phrase, usually 12 words): ')
			print('\nWIF: '+bip39(a,84,2)+'\n')
		case '8':
			a=input('Enter Base58Check encoded string: ')
			print('\n'+b58dec(a)+'\n')
		case '9':
			a=input('Enter hex string: ')
			print('\n'+b58enc(a)+'\n')
		case 'a':
			a=input('Enter hex string: ')
			open('output.bin','wb').write(hex_to_bytes(a))
			print('\nWritten to output.bin file\n')
		case 'b':
			a=input('Enter filename [input.txt]: ')
			if a=='':
				a='input.txt'
			print('\nLines count: '+str(count_lines(a))+'\n')
		case 'c':
			a=input('Enter hex: ')
			print('\nInteger: '+str(hex_to_int(a))+'\n')
		case 'd':
			a=input('Enter int: ')
			print('\nHex: '+int_to_hex(a)+'\n')
		case 'e':
			a=input('Enter public key: ')
			print('\nAddress: '+pubkey_to_addr(a)+'\n')
		case 'f':
			a=input('Enter private key in hex: ')
			print('\nWIF: '+pvk_to_wif2(a)+'\n')
		case 'g':
			a=input('Enter private key in hex: ')
			print('\nPublic key: '+pvk_to_wif2(a)+'\n')
		case 'h':
			a=input('Enter string: ')
			print('\nHex: '+str_to_hex(a)+'\n')
		case 'i':
			a=input('Enter WIF: ')
			print('\nPrivate key: '+wif_to_pvk(a)+'\n')
		case '':
			exit(0)
