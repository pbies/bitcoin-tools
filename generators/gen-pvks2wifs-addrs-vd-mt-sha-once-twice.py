#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
import base58
import hashlib
import sys

def int_to_bytes4(number, length): # in: int, int
	# length = zero-fill bytes
	return number.to_bytes(length,'big')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

tmp = 0
cnt = 1000
th=24
r=range(1,int(1e9+1))
l=len(r)
pbar=tqdm(total=l)

def go(x):
	global tmp, i
	x=int_to_bytes4(x, 32)
	#print(x)
	sha1=hashlib.sha256(x).hexdigest()
	shatmp=hashlib.sha256(x).digest()
	sha2=hashlib.sha256(shatmp).hexdigest()
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=sha1)
		hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=sha2)
	except:
		return
	pvk1=hdwallet1.private_key()
	pvk2=hdwallet2.private_key()
	wif1=pvk_to_wif2(pvk1)
	wif2=pvk_to_wif2(pvk2)
	w=f'{wif1}\n{hdwallet1.wif()}\n{hdwallet1.address("P2PKH")}\n{hdwallet1.address("P2SH")}\n{hdwallet1.address("P2TR")}\n{hdwallet1.address("P2WPKH")}\n{hdwallet1.address("P2WPKH-In-P2SH")}\n{hdwallet1.address("P2WSH")}\n{hdwallet1.address("P2WSH-In-P2SH")}\n\n'
	w+=f'{wif2}\n{hdwallet2.wif()}\n{hdwallet2.address("P2PKH")}\n{hdwallet2.address("P2SH")}\n{hdwallet2.address("P2TR")}\n{hdwallet2.address("P2WPKH")}\n{hdwallet2.address("P2WPKH-In-P2SH")}\n{hdwallet2.address("P2WSH")}\n{hdwallet2.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(w)
	outfile.flush()
	tmp=tmp+1
	if tmp%cnt==0:
		pbar.update(tmp)
		pbar.refresh()

outfile = open('output.txt','w')

if __name__=='__main__':
	with Pool(processes=th) as p, tqdm(total=l) as pbar:
		for result in p.imap_unordered(go, r, chunksize=1000):
			pass

	print('\a', end='', file=sys.stderr)
