#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD, BIP84HD
from tqdm import tqdm
import asyncio
import base58
import sys

hdwallet_bip32 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
hdwallet_bip84 = HDWallet(cryptocurrency=BTC, hd=BIP84HD)

inputfile=open('input.txt','r')
of=open('output.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

async def convert(pvk):
		try:
			hdwallet_bip32.from_private_key(private_key=pvk)
			hdwallet_bip84.from_private_key(private_key=pvk)
		except:
			return
		pvk1 = hdwallet_bip32.private_key()
		pvk2 = hdwallet_bip84.private_key()
		wif1 = pvk_to_wif2(pvk1)
		wif2 = pvk_to_wif2(pvk2)
		w = f'{wif1}\n{hdwallet_bip32.wif()}\n{hdwallet_bip32.address("P2PKH")}\n{hdwallet_bip32.address("P2SH")}\n{hdwallet_bip32.address("P2TR")}\n{hdwallet_bip32.address("P2WPKH")}\n{hdwallet_bip32.address("P2WPKH-In-P2SH")}\n{hdwallet_bip32.address("P2WSH")}\n{hdwallet_bip32.address("P2WSH-In-P2SH")}\n\n'
		w += f'{wif2}\n{hdwallet_bip84.wif()}\n{hdwallet_bip84.address("P2PKH")}\n{hdwallet_bip84.address("P2SH")}\n{hdwallet_bip84.address("P2TR")}\n{hdwallet_bip84.address("P2WPKH")}\n{hdwallet_bip84.address("P2WPKH-In-P2SH")}\n{hdwallet_bip84.address("P2WSH")}\n{hdwallet_bip84.address("P2WSH-In-P2SH")}\n\n'
		of.write(w)
		of.flush()

async def main():
	print('Reading...', flush=True)
	pvks=inputfile.read().splitlines()

	print('Writing...', flush=True)
	tasks = [convert(pvk) for pvk in tqdm(pvks)]
	await asyncio.gather(*tasks)

	print('\a', end='', file=sys.stderr)

asyncio.run(main())
