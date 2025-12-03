import base58
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from nacl.secret import SecretBox
from nacl.exceptions import CryptoError
# Encrypted data and parameters (assuming all are base58 encoded)
data = {
	"encrypted": "",
	"nonce": "",
	"salt": "",
	"iterations": 10000,
}
password = ''  # Replace with your actual password

# Decode from Base58
salt = base58.b58decode(data['salt'])
nonce = base58.b58decode(data['nonce'])
encrypted_data = base58.b58decode(data['encrypted'])
# Derive the key using PBKDF2 with SHA-256
kdf = PBKDF2HMAC(
	algorithm=hashes.SHA256(),
	length=32,
	salt=salt,
	iterations=data['iterations'],
	backend=default_backend()
)
key = kdf.derive(password.encode())
# Decrypt the data using PyNaCl's SecretBox
box = SecretBox(key)
try:
	decrypted = box.decrypt(encrypted_data, nonce)
	# Instead of attempting to decode as UTF-8, print the raw bytes or their hex representation
	print("Decrypted data (hex):", decrypted.hex())
except CryptoError as e:
	print(f"Decryption failed: {e}")
