#!/usr/bin/env python3

import os
import hashlib
import base58
import ecdsa

# Generowanie losowego klucza prywatnego
def generate_private_key():
    return os.urandom(32)

# Generowanie klucza publicznego z klucza prywatnego
def private_key_to_public_key(private_key):
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return b'\x04' + vk.to_string()

# Generowanie adresu Bitcoin z klucza publicznego
def public_key_to_address(public_key):
    sha256_1 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_1)
    hashed_public_key = ripemd160.digest()
    
    network_byte = b'\x00'
    hashed_public_key_with_network_byte = network_byte + hashed_public_key
    
    sha256_2 = hashlib.sha256(hashed_public_key_with_network_byte).digest()
    sha256_3 = hashlib.sha256(sha256_2).digest()
    checksum = sha256_3[:4]
    
    address_bytes = hashed_public_key_with_network_byte + checksum
    address = base58.b58encode(address_bytes)
    
    return address

# Generowanie i wyświetlanie przykładowego adresu Bitcoin
private_key = generate_private_key()
public_key = private_key_to_public_key(private_key)
address = public_key_to_address(public_key)

print("Private key:", private_key.hex())
print("Public key:", public_key.hex())
print("Address:", address.decode())
