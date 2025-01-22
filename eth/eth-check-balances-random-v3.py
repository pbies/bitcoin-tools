#!/usr/bin/env python3

from web3 import Web3
from tqdm.contrib.concurrent import process_map
from ecpy.curves import Curve
from Crypto.Hash import keccak
from tqdm import tqdm
import os

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

outfile = open("eth_addr.txt","a")
pvkfile = open("eth_pvks.txt","a")

def worker(key):
    bal=w3.eth.get_balance(w3.to_checksum_address(key),"latest")
    if bal>0:
        print("Found one!")
    outfile.write(key+" "+str(bal)+"\n")
    outfile.flush()

def bytes_to_int(bytes):
    return int.from_bytes(bytes,"big")

cnt=2001

lines=[]

print("Generating...")
for i in tqdm(range(1,cnt), total=cnt-1, unit=" pvks"):
    private_key=bytes_to_int(os.urandom(32))
    cv     = Curve.get_curve('secp256k1')
    pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

    concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
    k=keccak.new(digest_bits=256)
    eth_addr = '0x' + k.update(concat_x_y).digest()[-20:].hex()
    lines.append(eth_addr)
    pvkfile.write(hex(private_key)+" "+eth_addr+"\n")

print("Checking...")
process_map(worker, lines, max_workers=4, chunksize=3000)
