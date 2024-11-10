#!/usr/bin/env python3

# pip install cryptography

# $bitcoin$64$08a4bbd5fbd998e5a334cb31dc43c3a625872998b6ff5b3830f5ffe30ee8156b$16$0af493ab2796f208$73689$2$00$2$00
# 1Gj2KiTy9SFtuFSJECmpePseYchhkU3gXQ
# 046d6b657901000000:304b84653654a3d5900df6588d90d5081308a4bbd5fbd998e5a334cb31dc43c3a625872998b6ff5b3830f5ffe30ee8156b080af493ab2796f20800000000d91f010000

"""
304b84653654a3d5900df6588d90d50813 IV ?
08a4bbd5fbd998e5a334cb31dc43c3a625872998b6ff5b3830f5ffe30ee8156b mkey/salt?
08 len
0af493ab2796f208 mkey/salt?
00000000
d91f01 iterations = 73689 dec
0000
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from hdwallet import HDWallet
from hdwallet.symbols import BTC
import base58

def pvk_to_wif2(key_hex): # in: '0000... [64] out: b'5HpH...
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

# Decrypt a private key with AES using the mkey
def decrypt_private_key(mkey, encrypted_private_key, salt, iv):
	# Derive a key from mkey and salt using PBKDF2
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=salt,
		iterations=73689,
		backend=default_backend()
	)
	key = kdf.derive(mkey)

	# Set up the AES cipher for decryption in CBC mode
	cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
	decryptor = cipher.decryptor()
	
	# Decrypt and return the plaintext private key
	decrypted_private_key = decryptor.update(encrypted_private_key) + decryptor.finalize()
	return decrypted_private_key

# Example usage
mkey = bytes.fromhex('08a4bbd5fbd998e5a334cb31dc43c3a625872998b6ff5b3830f5ffe30ee8156b') # Master key as bytes
salt = bytes.fromhex('08a4bbd5fbd998e5a334cb31dc43c3a625872998b6ff5b3830f5ffe30ee8156b') # Salt used for KDF, should be the same as used in encryption
iv = bytes.fromhex('304b84653654a3d5900df6588d90d508')		# IV for CBC mode, should be the same as used in encryption ; 16 bytes!
encrypted_private_key = bytes.fromhex('08a4bbd5fbd998e5a334cb31dc43c3a625872998b6ff5b3830f5ffe30ee8156b')

# Decrypt the private key
decrypted_private_key = decrypt_private_key(mkey, encrypted_private_key, salt, iv)
print("Decrypted Private Key:", decrypted_private_key.hex())

hdwallet = HDWallet(symbol=BTC)
hdwallet.from_private_key(private_key=decrypted_private_key.hex())
wif=pvk_to_wif2(decrypted_private_key.hex()).decode()
print('WIF v1:', wif)
print('WIF v2:', hdwallet.wif())
"""
Decrypted Private Key: 5b6dec8a1285dac01511771b3fc826e715a447389c6fc1ed265d331a9d729f82
WIF v1: 5JWZ2GDEQbcSiB7RYdE9paa5b4sUGkYKwBQXX5BNfBQjV5F3bR6
WIF v2: KzHSLa8zB9mSUjdMLau3w1B1FN5mNXBGa8vqhjSnbWwkWbiaq5i1

Decrypted Private Key: 20a20dd97072ac8588ead9ce228dfbfc15a447389c6fc1ed265d331a9d729f82
WIF v1: 5J4f9Z9gXNfuRMUEAVQtww4z2tiRUn4MAjZRz9pj6H4XJCXN6vG
WIF v2: KxK9NkuKT4eiNVMB6tQUHTeajMFq3bsn1xr9HFwenHtYijBJKrBi
"""
