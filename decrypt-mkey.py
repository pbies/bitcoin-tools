#!/usr/bin/env python3

# pip install cryptography

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# Decrypt a private key with AES using the mkey
def decrypt_private_key(mkey, encrypted_private_key, salt, iv):
	# Derive a key from mkey and salt using PBKDF2
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=salt,
		iterations=100000,
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
mkey = b'your_mkey_here' # Master key as bytes
salt = os.urandom(16)	 # Salt used for KDF, should be the same as used in encryption
iv = os.urandom(16)		# IV for CBC mode, should be the same as used in encryption
encrypted_private_key = base64.b64decode('base64_encrypted_private_key_here')

# Decrypt the private key
decrypted_private_key = decrypt_private_key(mkey, encrypted_private_key, salt, iv)
print("Decrypted Private Key:", decrypted_private_key)
