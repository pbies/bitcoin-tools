#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from pprint import pprint
import random
import time

class Node:
	def __init__(self, data):
		self.left = None
		self.right = None
		self.data = data

def buildTree(addrs, start, end):
	if (start > end):
		return None

	mid = int(start + (end - start) / 2)
	node = Node(addrs[mid])

	node.left = buildTree(addrs, start, mid - 1)
	node.right = buildTree(addrs, mid + 1, end)

	return node

def search(root, key):
	if root is None:
		return None

	if root.data == key:
		return key

	if root.data < key:
		return search(root.right, key)

	return search(root.left, key)

def int_to_bytes4(number, length):
	return number.to_bytes(length,'big')

def f(wif):
	print('\nFound WIF: '+wif, flush=True)
	o=open('KEYFOUND.txt','a')
	o.write(wif+'\n')
	o.flush()
	o.close()

hdwallet = HDWallet(symbol=BTC)

a=[]

print('Loading addresses...')

start = time.time()
a_all=open('addrs-with-bal.txt','r').readlines()
end = time.time()

print(f'It took {end-start:.3f} seconds.')
print('Filtering addresses...')

start = time.time()
for i in tqdm(a_all):
	i=i.strip()
	if (i[0]=='1') or (i[0]=='3') or (i[0:3]=='bc1'):
		a.append(i)
end = time.time()

print(f'Added addresses: {len(a)}\nOmitted addresses: {len(a_all)-len(a)}')
print(f'It took {end-start:.3f} seconds.')

print('Sorting addresses...')
start = time.time()
a.sort()
end = time.time()
print(f'It took {end-start:.3f} seconds.')

print('Building tree...')
start = time.time()
tree=buildTree(a,0,len(a)-1)
end = time.time()

print(f'It took {end-start:.3f} seconds.')
print('Generating pvks...')

for i in tqdm(range(1,1000000001)):
	p=int_to_bytes4(i,32).hex()
	hdwallet.from_private_key(private_key=p)

	a1=hdwallet.p2pkh_address()
	a2=hdwallet.p2sh_address()
	a3=hdwallet.p2wpkh_address()

	if search(tree, a1)==a1:
		f(hdwallet.wif())
	if search(tree, a2)==a2:
		f(hdwallet.wif())
	if search(tree, a3)==a3:
		f(hdwallet.wif())
