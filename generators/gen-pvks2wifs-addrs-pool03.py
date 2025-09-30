#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.hds import BIP84HD
from tqdm import tqdm
import sys, os, base58
from multiprocessing import Pool

th=16

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(nul):
	pvk=os.urandom(32).hex()
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=pvk)
		wif=pvk_to_wif2(pvk)
	except:
		return
	a=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	f.write(a)
	f.flush()

if __name__ == '__main__':
	f = open('output.txt', 'a')
	r = list(range(0, int(sys.argv[1])))
	max_ = len(r)

	c=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, r, chunksize=1000):
			if c%1000==0:
				pbar.update(1000)
				pbar.refresh()
			c=c+1

	print('\a', end='', file=sys.stderr)
