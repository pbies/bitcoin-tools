from mnemonic import Mnemonic
import binascii
# Decrypted data in hex
decrypted_hex = 'your_128_byte_string'
# Convert hex to bytes
entropy_bytes = binascii.unhexlify(decrypted_hex)
# Generate mnemonic from the entropy bytes
mnemo = Mnemonic("english")
mnemonic = mnemo.to_mnemonic(entropy_bytes)
print("Mnemonic:", mnemonic)
