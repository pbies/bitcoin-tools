import ecdsa
import hashlib
import base58


with open("my_private_key.txt", "r") as f:    #Input file path
      for line in f:

                  #Convert hex private key to bytes
         private_key = bytes.fromhex(line)      

                  #Derivation of the private key
         signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
         verifying_key = signing_key.get_verifying_key()

         public_key = bytes.fromhex("04") + verifying_key.to_string()

                 #Hashes of public key
         sha256_1 = hashlib.sha256(public_key)
         ripemd160 = hashlib.new("ripemd160")
         ripemd160.update(sha256_1.digest())

                 #Adding prefix to identify Network
         hashed_public_key = bytes.fromhex("00") + ripemd160.digest()

                 #Checksum calculation
         checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
         checksum = checksum_full[:4]

                 #Adding checksum to hashpubkey         
         bin_addr = hashed_public_key + checksum

                 #Encoding to address
         address = str(base58.b58encode(bin_addr))
         final_address = address[2:-1]

         print(final_address)

         with open("my_addresses.txt", "a") as i:
            i.write(final_address)
