#!/usr/bin/env python3

from web3 import Web3
from tqdm.contrib.concurrent import process_map
from ecpy.curves import Curve
from ecpy.keys import ECPublicKey, ECPrivateKey
from sha3 import keccak_256
from tqdm import tqdm
import random

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

infile  = open('input.txt','r')
outfile = open('output.txt','a')

lines=[]

rt=[]

lines=infile.readlines()
lines = [x.strip() for x in lines]
cnt=len(lines)

pbar=tqdm(total=cnt)

for i in lines:
	cv = Curve.get_curve('secp256k1')
	i=int(i,16)
	pv_key = ECPrivateKey(i, cv)
	pu_key = pv_key.get_public_key()

	concat_x_y = pu_key.W.x.to_bytes(32, byteorder='big') + pu_key.W.y.to_bytes(32, byteorder='big')
	eth_addr = '0x' + keccak_256(concat_x_y).digest()[-20:].hex()

	a=w3.to_checksum_address(eth_addr)
	bal=w3.eth.get_balance(a,"latest")
	if bal>=1000000000000000: # 1 mETH = 10^15 wei
		print("\n\aFound one! pvk: "+hex(i)+" addr: "+a+" bal: "+str(bal))
		outfile.write(hex(j)+" "+a+" balance: "+str(bal)+"\n")
		outfile.flush()
	pbar.update(1)

pbar.close()
