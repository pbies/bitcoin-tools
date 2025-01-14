#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.hds import BIP84HD
from tqdm import tqdm
import sys, os, base58

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

if __name__ == '__main__':
	f = open('output.txt', 'a')
	for i in tqdm(range(0, int(sys.argv[1]))):
		pvk=os.urandom(32).hex()
		try:
			hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=pvk)
			hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(private_key=pvk)
		except:
			continue
		wif=pvk_to_wif2(pvk)
		a=wif+'\n'+hdwallet1.wif()+'\n'+hdwallet1.address("P2PKH")+'\n'+hdwallet1.address("P2SH")+'\n'+hdwallet1.address("P2TR")+'\n'+hdwallet1.address("P2WPKH")+'\n'+hdwallet1.address("P2WPKH-In-P2SH")+'\n'+hdwallet1.address("P2WSH")+'\n'+hdwallet1.address("P2WSH-In-P2SH")+'\n\n'
		b=wif+'\n'+hdwallet2.wif()+'\n'+hdwallet2.address("P2PKH")+'\n'+hdwallet2.address("P2SH")+'\n'+hdwallet2.address("P2TR")+'\n'+hdwallet2.address("P2WPKH")+'\n'+hdwallet2.address("P2WPKH-In-P2SH")+'\n'+hdwallet2.address("P2WSH")+'\n'+hdwallet2.address("P2WSH-In-P2SH")+'\n\n'
		f.write(a)
		f.write(b)
		f.flush()

	print('\a', end='', file=sys.stderr)
