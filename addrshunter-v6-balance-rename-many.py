#!/usr/bin/env python3

import os
import requests
import sys
import time
import json

readlength=10*1024*1024

token='7c5e4d2677c5488ca288639d8aab9d6b'

# https://api.blockcypher.com/v1/btc/main/addrs/14jt9AzqeM1TX3oQCGWkQbtfeUYih3o56W/balance?token=7c5e4d2677c5488ca288639d8aab9d6b

magic = b'name'
magiclen = len(magic)

def bytes_to_int(bytes):
	return int.from_bytes(bytes,'big')

correct=[33,34,42]

for infile in os.listdir('.'):
	if os.path.isfile(infile) and infile[-4:]=='.dat':
		with open(infile, 'rb') as f:
			print(infile,end='',flush=True)
			d={}
			br=False
			while True:
				data = f.read(readlength)
				if not data:
					print(flush=True)
					br=True
					break
				pos = 0
				while True:
					pos = data.find(magic, pos)
					if pos == -1:
						if d:
							maxk=max(d,key=d.get)
							maxb=max(d.values())
							if os.path.isfile(infile):
								os.rename(infile,maxk+' - '+str(int(maxb)/100000000)+' BTC.dat')
						print(flush=True)
						br=True
						break
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
						#r=requests.get('https://blockchain.info/q/addressbalance/'+k)
						print('.',end='',flush=True)
						if k not in d:
							r=requests.get('https://api.blockcypher.com/v1/btc/main/addrs/'+k+'/balance?token='+token)
							time.sleep(2)
							if r.status_code==429:
								print('\nToo many requests! Wait for some time...')
								exit(1)
							if not r.status_code==200:
								print('\nFailed with '+infile+' - error code: '+str(r.status_code))
								continue
							j=json.loads(r.text)
							b=j['balance']
							d[k]=b
							br=False
					pos += 1
				if br==True:
					break

				if len(data) == readlength:
					f.seek(f.tell() - (32 + magiclen))
