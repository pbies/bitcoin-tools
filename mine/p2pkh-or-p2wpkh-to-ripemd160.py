import bit
print(base58.b58decode_check(P2PKH_address)[1:].hex())
print(bytes(base32.decode(P2WPKH_address)[1]).hex())
