#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet tqdm web3 bip32utils

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from os import system, name
from pprint import pprint
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
import os
import pprint
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
	cnt=sum(1 for line in open(i))
	f2=open(o,'w')
	for line in tqdm(f1, total=cnt, unit=" lines"):
		x=line.rstrip('\n').encode()
		sha=hashlib.sha256(x).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		i=h+b" 0 # "+x+b'\n'
		f2.write(i.decode())
	f1.close()
	f2.flush()
	f2.close()
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

def bytes_to_hex(b):
	return b.hex()

def bytes_to_hex2(b):
	return hex(b)

def count_lines(file):
	return sum(1 for line in open(file, 'r'))

def hex_to_int(hex):
	return int(hex, 16)

def int_to_hex(i):
	return hex(int(i))

def int_to_bytes3(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def pubkey_to_addr(pk):
	if (ord(bytearray.fromhex(pk[-2:])) % 2 == 0):
		public_key_compressed = '02'
	else:
		public_key_compressed = '03'
	public_key_compressed += pk[2:66]
	hex_str = bytearray.fromhex(public_key_compressed)
	sha = hashlib.sha256()
	sha.update(hex_str)
	key_hash = hashlib.new('ripemd160',sha.digest()).hexdigest()
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

def pvk_bin_to_addr(pvk):
	signing_key = ecdsa.SigningKey.from_string(pvk, curve = ecdsa.SECP256k1)
	verifying_key = signing_key.get_verifying_key()
	public_key = bytes.fromhex("04") + verifying_key.to_string()
	sha256_1 = hashlib.sha256(public_key)
	ripemd160 = hashlib.new("ripemd160")
	ripemd160.update(sha256_1.digest())
	hashed_public_key = bytes.fromhex("00") + ripemd160.digest()
	checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
	checksum = checksum_full[:4]
	bin_addr = hashed_public_key + checksum
	return base58.b58encode(bin_addr).decode()

def str_to_hex(text):
	return binascii.hexlify(text.encode()).decode()

def wif_to_pvk(s):
	return base58.b58decode_check(s).hex()

def sha256binary(a,b):
	i=open(a,'rb')
	d=i.read()
	h=hashlib.sha256(d).digest()
	o=open(b,'wb')
	o.write(h)
	i.close()
	o.flush()
	o.close()
	return

def ripemd160binary(a,b):
	i=open(a,'rb')
	d=i.read()
	h=hashlib.new('ripemd160',d).digest()
	o=open(b,'wb')
	o.write(h)
	i.close()
	o.flush()
	o.close()
	return

def sha256hex(h):
	return hashlib.sha256(hex_to_bytes(h)).hexdigest()

def ripemd160hex(h):
	t=hashlib.new('ripemd160',hex_to_bytes(h)).hexdigest()
	return t

def hex_to_string(h):
	return bytes.fromhex(h).decode('utf-8')

clear()
while True:
	print('Tool for cc v0.41 (C) 2023-2024 Aftermath @Tzeeck')
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
	print('g. private key hex to public key')
	print('h. string to hex')
	print('i. WIF to private key hex')
	print('j. binary SHA256 (files)')
	print('k. hex SHA256 (a file)')
	print('l. binary RIPEMD160 (files)')
	print('m. hex RIPEMD160 (a file)')
	print('n. generate set')
	print('o. get SHA256 of hex (hex converted to binary)')
	print('p. get RIPEMD160 of hex (hex converted to binary)')
	print('q. string to address')
	print('r. address to string')
	print('s. make hash160 of public key hex')
	print('t. hex to string')
	print('u. bytes (file) to hex')
	print('v. address to public key')
	print('w. private key integer to WIF')
	print('x. private key integer to address')
	print('y. seed hex to HDWallet')
	print('z. private key hex to HDWallet')
	print('A. generate HD wallet')
	print()
	m=input('Select option or enter empty to quit: ')

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
			print('\nWIF: '+pvk_to_wif2(a).decode('ascii')+'\n')
		case 'g':
			a=input('Enter private key in hex: ')
			print('\nPublic key: '+pvk_to_pubkey(hex_to_bytes(a))+'\n')
		case 'h':
			a=input('Enter string: ')
			print('\nHex: '+str_to_hex(a)+'\n')
		case 'i':
			a=input('Enter WIF: ')
			print('\nPrivate key: '+wif_to_pvk(a)+'\n')
		case 'j':
			a=input('Enter input filename [input.bin]: ')
			b=input('Enter output filename [output.bin]: ')
			if a=='':
				a='input.bin'
			if b=='':
				b='output.bin'
			sha256binary(a,b)
		case 'k':
			a=input('Enter input filename [input.bin]: ')
			if a=='':
				a='input.bin'
			i=open(a,'rb')
			d=i.read()
			print('\nSHA256: '+hashlib.sha256(d).hexdigest()+'\n')
			i.close()
		case 'l':
			a=input('Enter input filename [input.bin]: ')
			b=input('Enter output filename [output.bin]: ')
			if a=='':
				a='input.bin'
			if b=='':
				b='output.bin'
			ripemd160binary(a,b)
		case 'm':
			a=input('Enter input filename [input.bin]: ')
			if a=='':
				a='input.bin'
			i=open(a,'rb')
			d=i.read()
			h=hashlib.new('ripemd160',d).hexdigest()
			print('\nRIPEMD160: '+h+'\n')
			i.close()
		case 'n':
			pvk=os.urandom(32)
			print('\nPrivate key: '+pvk.hex())
			print('WIF        : '+pvk_to_wif2(pvk.hex()).decode('ascii'))
			print('Public key : '+pvk_to_pubkey(pvk))
			print('Address    : '+pubkey_to_addr(pvk_to_pubkey(pvk)))
			print()
		case 'o':
			h=input('Enter hex: ')
			print('\nSHA256: '+sha256hex(h))
			print()
		case 'p':
			h=input('Enter hex: ')
			print('\nRIPEMD160: '+ripemd160hex(h))
			print()
		case 'q':
			h=input('Enter string (up to 20 chars): ')
			if len(h) > 20:
				print('Too long!')
			else:
				h=b'\x00'+str.encode(h)
				while len(h)<21:
					h=h+b'\x20'
				print('\nAddress: '+base58.b58encode_check(h).decode('utf-8'))
				print()
		case 'r':
			s=input('Enter address: ')
			print('\nString: '+base58.b58decode_check(s).decode('utf-8'))
			print()
		case 's':
			h=input('Enter public key: ')
			print('\nHASH160: '+ripemd160hex(sha256hex(h)))
			print()
		case 't':
			a=input('Enter hex: ')
			try:
				print('\nString: '+hex_to_string(a)+'\n')
			except:
				print('\nNot UTF-8 printable bytes, can\'t convert!\n')
		case 'u':
			a=input('Enter input filename [input.bin]: ')
			if a=='':
				a='input.bin'
			i=open(a,'rb')
			d=i.read()
			print('\nHex: '+d.hex())
			print()
			i.close()
		case 'v':
			a=input('Enter address: ')
			req = ('https://blockchain.info/q/pubkeyaddr/' + a)
			resp = requests.get(req)
			if resp.status_code == 404: print('\nNot found\n')
			if resp.status_code == 200: print('\nPublic key:\n'+resp.text+'\n')
		case 'w':
			i=input('Enter integer: ')
			h=hex(int(i))[2:]
			while len(h)<64:
				h='0'+h
			if len(h)<66:
				h='80'+h
			p=bytes.fromhex(h)
			b=base58.b58encode_check(p)
			print((b'\nWIF: '+b+b'\n').decode('utf-8'))
		case 'x':
			i=input('Enter integer: ')
			b=int_to_bytes3(int(i),32)
			a=pvk_bin_to_addr(b)
			print(f'\nAddress: {a}\n')
		case 'y':
			j=input('Enter seed hex: ')
			hdwallet = HDWallet(symbol=BTC)
			hdwallet.from_seed(seed=j)
			d=hdwallet.dumps()
			print()
			pprint(d)
			print()
		case 'z':
			j=input('Enter private key hex: ')
			hdwallet = HDWallet(symbol=BTC)
			hdwallet.from_private_key(private_key=j)
			d=hdwallet.dumps()
			print()
			pprint(d)
			print()
		case 'A':
			hdwallet = HDWallet(symbol=BTC)
			r=hex(random.randint(0,2**512))[2:]
			r='0'*(128-len(r))+r
			hdwallet.from_seed(seed=r)
			hdwallet.from_path(path="m/44'/0'/0'/0/0")
			pp = pprint.PrettyPrinter(depth=4)
			d = hdwallet.dumps()
			print('\n'+pp.pformat(d)+'\n')
		case '':
			exit(0)
