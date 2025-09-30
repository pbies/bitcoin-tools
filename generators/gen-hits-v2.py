#!/usr/bin/env python3

from ecpy.curves import Curve
from Crypto.Hash import keccak
from tqdm import tqdm

f=open("hits.txt","wb")
g=open("pvks.txt","w")

cnt=1024*1024

for private_key in tqdm(range(1,cnt), total=cnt, unit=" pvks"):
    cv     = Curve.get_curve('secp256k1')
    pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

    concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
    k=keccak.new(digest_bits=256)
    eth_addr = '0x' + k.update(concat_x_y).digest()[-20:].hex()

    f.write(str.encode(eth_addr)+b"\n")
    g.write(hex(private_key)+"\n")

f.flush()
f.close()
