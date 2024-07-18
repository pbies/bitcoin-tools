#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

# It does not work as process runs out of resources.

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
import pprint
import random
import time
from tqdm.contrib.concurrent import process_map

class Node:
	def __init__(self, data):
		self.left = None
		self.right = None
		self.data = data

	def insert(self, data):
		if self.data:
			if data < self.data:
				if self.left is None:
					self.left = Node(data)
				else:
					self.left.insert(data)
			elif data > self.data:
					if self.right is None:
						self.right = Node(data)
					else:
						self.right.insert(data)
		else:
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
	if root is None or root.data == key:
		return root

	if root.data < key:
		return search(root.right, key)

	return search(root.left, key)

def int_to_bytes4(number, length): # in: int, int
	return number.to_bytes(length,'big')

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
	if i[0]=='1' or i[0]=='3' or i[0:2]=='bc1':
		a.append(i)
end = time.time()

print(f'It took {end-start:.3f} seconds.')
print('Building tree...')

start = time.time()
tree=buildTree(a,0,len(a)-1)
end = time.time()

print(f'It took {end-start:.3f} seconds.')
print('Generating pvks...')

def go(i):
	p=int_to_bytes4(i,32).hex()
	hdwallet.from_private_key(private_key=p)

	a1=hdwallet.p2pkh_address()
	a2=hdwallet.p2sh_address()
	a3=hdwallet.p2wpkh_address()
	a4=hdwallet.p2wpkh_in_p2sh_address()
	a5=hdwallet.p2wsh_address()
	a6=hdwallet.p2wsh_in_p2sh_address()

	if search(tree, a1) is not None:
		print('\n'+hdwallet.wif())
	if search(tree, a2) is not None:
		print('\n'+hdwallet.wif())
	if search(tree, a3) is not None:
		print('\n'+hdwallet.wif())
	if search(tree, a4) is not None:
		print('\n'+hdwallet.wif())
	if search(tree, a5) is not None:
		print('\n'+hdwallet.wif())
	if search(tree, a6) is not None:
		print('\n'+hdwallet.wif())

process_map(go, range(1,1000000001), max_workers=4, chunksize=100, ascii=False)
