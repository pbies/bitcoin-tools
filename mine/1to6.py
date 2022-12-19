# -*- coding: utf-8 -*-
"""

@author: iceland
"""
import bit
import random
import bitcoinlib
from bit import Key
###############################################################################
p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

###############################################################################
# Constants Based on Cube root of 1
lmda  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140
lmda2 = 0x0000000000000000000000000000000000000000000000000000000000000001  # lmda*lmda

beta  = 0x7ae96a2b657c07106e64479eac3434e99cf0497512f58995c1396c28719501ee
beta2 = 0x851695d49a83f8ef919bb86153cbcb16630fb68aed0a766a3ec693d68e6afa40      # beta*beta
###############################################################################

def one_to_6pubkey(upub_hex):
    if len(upub_hex) < 70: print('Please provide full Uncompressed Pubkey in hex'); exit()
    x = int(upub_hex[2:66], 16)
    y = int(upub_hex[66:], 16)
    print('PubkeyU1 : ', '04' + hex(x)[2:].zfill(64) + hex(y)[2:].zfill(64))
    print('PubkeyU2 : ', '04' + hex(x * beta % p)[2:].zfill(64) + hex(y)[2:].zfill(64))
    print('PubkeyU3 : ', '04' + hex(x * beta2 % p)[2:].zfill(64) + hex(y)[2:].zfill(64))
    print('PubkeyU4 : ', '04' + hex(x)[2:].zfill(64) + hex(p - y)[2:].zfill(64))
    print('PubkeyU5 : ', '04' + hex(x * beta % p)[2:].zfill(64) + hex(p - y)[2:].zfill(64))
    print('PubkeyU6 : ', '04' + hex(x * beta2 % p)[2:].zfill(64) + hex(p - y)[2:].zfill(64))

    print('PubkeyC1 : ', '03' + hex(x)[2:].zfill(64))
    print('PubkeyC2 : ', '03' + hex(x * beta % p)[2:].zfill(64))
    print('PubkeyC3 : ', '03' + hex(x * beta2 % p)[2:].zfill(64))
    print('PubkeyC4 : ', '02' + hex(x)[2:].zfill(64))
    print('PubkeyC5 : ', '02' + hex(x * beta % p)[2:].zfill(64))
    print('PubkeyC6 : ', '02' + hex(x * beta2 % p)[2:].zfill(64))


def one_to_6privatekey(pvk_hex):
    pvk = int(pvk_hex, 16)
    print('PVK1 : ', hex(pvk)[2:].zfill(64))
    print('PVK2 : ', hex(pvk * lmda % N)[2:].zfill(64))
    print('PVK3 : ', hex(pvk * lmda2 % N)[2:].zfill(64))
    print('PVK4 : ', hex(N - pvk)[2:].zfill(64))
    print('PVK5 : ', hex(N - pvk * lmda % N)[2:].zfill(64))
    print('PVK6 : ', hex(N - pvk * lmda2 % N)[2:].zfill(64))


def pvk_to_24address(pvk_hex):
    pvk = int(pvk_hex, 16)
    print('PVK1 BTC Address : [Compressed  ]  ',
          bit.format.public_key_to_address(bit.Key.from_int(pvk)._pk.public_key.format(compressed=True)))
    print('PVK1 BTC Address : [Uncompressed]  ',
          bit.format.public_key_to_address(bit.Key.from_int(pvk)._pk.public_key.format(compressed=False)))
    print('PVK1 BTC Address : [Segwit      ]  ', bit.Key.from_int(pvk).segwit_address)
    print('PVK1 BTC Address : [Bech32      ]  ',
          bitcoinlib.keys.Address(bit.Key.from_int(pvk).public_key.hex(), encoding='bech32',
                                  script_type='p2wpkh').address)
    print('PVK1 BTC PubKey  : [Compressed  ]  ',
          Key.from_hex(hex(pvk)[2:])._pk.public_key.format(compressed=True).hex())

    print('PVK2 BTC Address : [Compressed  ]  ',
          bit.format.public_key_to_address(bit.Key.from_int(pvk * lmda % N)._pk.public_key.format(compressed=True)))
    print('PVK2 BTC Address : [Uncompressed]  ',
          bit.format.public_key_to_address(bit.Key.from_int(pvk * lmda % N)._pk.public_key.format(compressed=False)))
    print('PVK2 BTC Address : [Segwit      ]  ', bit.Key.from_int(pvk * lmda % N).segwit_address)
    print('PVK2 BTC Address : [Bech32      ]  ',
          bitcoinlib.keys.Address(bit.Key.from_int(pvk * lmda % N).public_key.hex(), encoding='bech32',
                                  script_type='p2wpkh').address)
    print('PVK2 BTC PubKey  : [Compressed  ]  ',
          Key.from_hex(hex(pvk * lmda % N)[2:])._pk.public_key.format(compressed=True).hex())

    print('PVK3 BTC Address : [Compressed  ]  ',
          bit.format.public_key_to_address(bit.Key.from_int(pvk * lmda2 % N)._pk.public_key.format(compressed=True)))
    print('PVK3 BTC Address : [Uncompressed]  ',
          bit.format.public_key_to_address(bit.Key.from_int(pvk * lmda2 % N)._pk.public_key.format(compressed=False)))
    print('PVK3 BTC Address : [Segwit      ]  ', bit.Key.from_int(pvk * lmda2 % N).segwit_address)
    print('PVK3 BTC Address : [Bech32      ]  ',
          bitcoinlib.keys.Address(bit.Key.from_int(pvk * lmda2 % N).public_key.hex(), encoding='bech32',
                                  script_type='p2wpkh').address)
    print('PVK3 BTC PubKey  : [Compressed  ]  ',
          Key.from_hex(hex(pvk * lmda2 % N)[2:])._pk.public_key.format(compressed=True).hex())

    print('PVK4 BTC Address : [Compressed  ]  ',
          bit.format.public_key_to_address(bit.Key.from_int(N - pvk)._pk.public_key.format(compressed=True)))
    print('PVK4 BTC Address : [Uncompressed]  ',
          bit.format.public_key_to_address(bit.Key.from_int(N - pvk)._pk.public_key.format(compressed=False)))
    print('PVK4 BTC Address : [Segwit      ]  ', bit.Key.from_int(N - pvk).segwit_address)
    print('PVK4 BTC Address : [Bech32      ]  ',
          bitcoinlib.keys.Address(bit.Key.from_int(N - pvk).public_key.hex(), encoding='bech32',
                                  script_type='p2wpkh').address)
    print('PVK4 BTC PubKey  : [Compressed  ]  ',
          Key.from_hex(hex(N - pvk)[2:])._pk.public_key.format(compressed=True).hex())

    print('PVK5 BTC Address : [Compressed  ]  ',
          bit.format.public_key_to_address(bit.Key.from_int(N - pvk * lmda % N)._pk.public_key.format(compressed=True)))
    print('PVK5 BTC Address : [Uncompressed]  ', bit.format.public_key_to_address(
        bit.Key.from_int(N - pvk * lmda % N)._pk.public_key.format(compressed=False)))
    print('PVK5 BTC Address : [Segwit      ]  ', bit.Key.from_int(N - pvk * lmda % N).segwit_address)
    print('PVK5 BTC Address : [Bech32      ]  ',
          bitcoinlib.keys.Address(bit.Key.from_int(N - pvk * lmda % N).public_key.hex(), encoding='bech32',
                                  script_type='p2wpkh').address)
    print('PVK5 BTC PubKey  : [Compressed  ]  ',
          Key.from_hex(hex(N - pvk * lmda % N)[2:])._pk.public_key.format(compressed=True).hex())

    print('PVK6 BTC Address : [Compressed  ]  ', bit.format.public_key_to_address(
        bit.Key.from_int(N - pvk * lmda2 % N)._pk.public_key.format(compressed=True)))
    print('PVK6 BTC Address : [Uncompressed]  ', bit.format.public_key_to_address(
        bit.Key.from_int(N - pvk * lmda2 % N)._pk.public_key.format(compressed=False)))
    print('PVK6 BTC Address : [Segwit      ]  ', bit.Key.from_int(N - pvk * lmda2 % N).segwit_address)
    print('PVK6 BTC Address : [Bech32      ]  ',
          bitcoinlib.keys.Address(bit.Key.from_int(N - pvk * lmda2 % N).public_key.hex(), encoding='bech32',
                                  script_type='p2wpkh').address)
    print('PVK6 BTC PubKey  : [Compressed  ]  ',
          Key.from_hex(hex(N - pvk * lmda2 % N)[2:])._pk.public_key.format(compressed=True).hex())


def do_all(pvk_hex):
    one_to_6privatekey(pvk_hex)
    if pvk_hex > '0' and pvk_hex < 'fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141':
        one_to_6pubkey(bit.Key.from_hex(pvk_hex)._pk.public_key.format(compressed=False).hex())
        pvk_to_24address(pvk_hex)
    else:
        print('Sorry, no further information is available \n')
        print(hex(0)[2:])


datatype_onscreen = input(
    "[+] Please select your data type: \n{+} Enter 1 for ECDSA PRIVATE KEY \n{+} Enter 2 for PUBLIC KEY \n{+} Enter 3 for RANDOM \n==> ")
if datatype_onscreen == "1":
    privkey = input("\n[+] Please enter ECDSA PRIVATE KEY \n{+}==> ")
    do_all(privkey)
elif datatype_onscreen == "2":
    pubkey = input("\n[+] Please enter Uncompressed PUBLIC KEY \n{+}==> ")
    print('\n')
    one_to_6pubkey(pubkey)
    print('\n')
elif datatype_onscreen == "3":
    print('\n')
    do_all(hex(random.randrange(904625697166532776746648320380374280103671755200316906558262375061821325312,115792089237316195423570985008687907852837564279074904382605163141518161494337))[2:])
    print('\n')
else:
    print('Goodbye \n')
    exit()


