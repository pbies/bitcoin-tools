#!/usr/bin/python3

import json
import os
import requests
import sys
import time

readlength=10*1024*1024
token='7c5e4d2677c5488ca288639d8aab9d6b'
correct=[33,34,42]
magic = b'name'
magiclen = len(magic)

# https://api.blockcypher.com/v1/btc/main/addrs/14jt9AzqeM1TX3oQCGWkQbtfeUYih3o56W/balance?token=7c5e4d2677c5488ca288639d8aab9d6b

def bytes_to_int(bytes):
	return int.from_bytes(bytes,'big')

def get_balance(k):
	r=requests.get('https://api.blockcypher.com/v1/btc/main/addrs/'+k+'/balance?token='+token)
	#r=requests.get('https://blockchain.info/q/addressbalance/'+k)
	time.sleep(3)
	if r.status_code==429:
		print('\nToo many requests! Wait for some time...')
		exit(1)
	if not r.status_code==200:
		print('\nFailed with '+infile+' - error code: '+str(r.status_code))
		return None
	j=json.loads(r.text)
	b=j['balance']
	return b

def get_balances(filename):
	print(filename,end='')
	f=open(filename,'rb')
	d={}
	while True:
		data = f.read(readlength)
		if not data:
			break
		pos = 0
		while True:
			pos = data.find(magic, pos)
			if pos == -1:
				return d
			print('.',end='',flush=True)
			key_offset = pos + magiclen
			cnt=bytes_to_int(data[key_offset:key_offset+1])
			if cnt in correct:
				key_data = data[key_offset+1:key_offset + cnt+1]
				if b'\n' in key_data or b'\x0d' in key_data or b'\x00' in key_data:
					pos += 1
					continue
				try:
					k=key_data.decode('utf-8')
				except:
					pass
				if k not in d:
					d[k]=get_balance(k)
			pos+=1
			if len(data) == readlength:
				print('test')
				f.seek(f.tell() - (32 + magiclen))

for infile in os.listdir('.'):
	if os.path.isfile(infile) and infile[-4:]=='.dat':
		bals=get_balances(infile)
		if bals:
			maxk=max(bals,key=bals.get)
			maxb=max(bals.values())
			os.rename(infile,maxk+' - '+str(int(maxb)/100000000)+' BTC.dat')
			print('renamed',flush=True)
		else:
			print(' not renamed! No addresses inside!')
