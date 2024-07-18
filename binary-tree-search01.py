#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
import pprint
import random
from tqdm import tqdm

hdwallet = HDWallet(symbol=BTC)

a=[]

print('Loading addresses...')

a_all=open('addrs-with-bal.txt','r').readlines()

print('Filtering addresses...')

for i in tqdm(a_all):
	i=i.strip()
	if i[0]=='1' or i[0]=='3' or i[0:2]=='bc1':
		a.append(i)

def int_to_bytes4(number, length): # in: int, int
	return number.to_bytes(length,'big')

print('Generating pvks...')

for i in tqdm(range(1,1000000001)):
	p=int_to_bytes4(i,32).hex()
	hdwallet.from_private_key(private_key=p)

	a1=hdwallet.p2pkh_address()
	a2=hdwallet.p2sh_address()
	a3=hdwallet.p2wpkh_address()
	a4=hdwallet.p2wpkh_in_p2sh_address()
	a5=hdwallet.p2wsh_address()
	a6=hdwallet.p2wsh_in_p2sh_address()

	if a1 in a or a2 in a or a3 in a or a4 in a or a5 in a or a6 in a:
		print('\n'+hdwallet.wif())
