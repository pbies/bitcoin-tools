#!/usr/bin/env python3

# Pool is really faster than process_map

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.entropies import BIP39Entropy
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import sys

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	k=k.strip()
	try:
		hdwallet.from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=k))
		tmp1=hdwallet
	except:
		tmp1=None
	try:
		hdwallet.from_private_key(private_key=k)
		tmp2=hdwallet
	except:
		tmp2=None
	try:
		hdwallet.from_seed(seed=BIP39Seed(k))
		tmp3=hdwallet
	except:
		tmp3=None
	try:
		hdwallet.from_wif(wif=k)
		tmp4=hdwallet
	except:
		tmp4=None
	try:
		hdwallet.from_xprivate_key(xprivate_key=k)
		tmp5=hdwallet
	except:
		tmp5=None
	try:
		hdwallet.from_entropy(entropy=BIP39Entropy(k))
		tmp6=hdwallet
	except:
		tmp6=None
	try:
		k=base58.b58decode_check(k)[0:].hex()[2:]
		hdwallet.from_private_key(private_key=k)
		tmp7=hdwallet
	except:
		tmp7=None

	for i in [tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7]:
		if i!=None:
			pvk=i.private_key()
			wif=pvk_to_wif2(pvk)
			r=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
			outfile.write(r)
			outfile.flush()

infile = open('input.txt','r')

print('Reading...')
lines = infile.read().splitlines()
lines = [x.strip() for x in lines]

th=24
max_=len(lines)

print('Writing...')
# process_map(go, lines, max_workers=24, chunksize=1000)
outfile = open('output.txt','w')
i=0
with Pool(processes=th) as p, tqdm(total=max_) as pbar:
	for result in p.imap(go, lines):
		if i%1000==0:
			pbar.update(1000)
			pbar.refresh()
		i=i+1

print('\a', end='', file=sys.stderr)
