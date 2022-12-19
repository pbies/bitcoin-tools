#!/usr/bin/env python

import argparse
import base58
import binascii
import ecdsa
import getpass
import hashlib
import struct
import sys

crypter = None

debug = 0

try:
    from Crypto.Cipher import AES
    crypter = 'pycrypto'
except:
    pass

class Crypter_pycrypto( object ):
    def SetKeyFromPassphrase(self, vKeyData, vSalt, nDerivIterations, nDerivationMethod):
        data = vKeyData + vSalt
        for i in range(nDerivIterations):
            data = hashlib.sha512(data).digest()
        self.SetKey(data[0:32])
        self.SetIV(data[32:32+16])
        return len(data)

    def SetKey(self, key):
        self.chKey = key

    def SetIV(self, iv):
        self.chIV = iv[0:16]

    def Encrypt(self, data):
        return AES.new(self.chKey,AES.MODE_CBC,self.chIV).encrypt(data)[0:32]
 
    def Decrypt(self, data):
        return AES.new(self.chKey,AES.MODE_CBC,self.chIV).decrypt(data)[0:32]

try:
    if not crypter:
        import ctypes
        import ctypes.util
        ssl = ctypes.cdll.LoadLibrary (ctypes.util.find_library ('ssl') or 'libeay32')
        crypter = 'ssl'
except:
    pass

class Crypter_ssl(object):
    def __init__(self):
        self.chKey = ctypes.create_string_buffer (32)
        self.chIV = ctypes.create_string_buffer (16)

    def SetKeyFromPassphrase(self, vKeyData, vSalt, nDerivIterations, nDerivationMethod):
        strKeyData = ctypes.create_string_buffer (vKeyData)
        chSalt = ctypes.create_string_buffer (vSalt)
        return ssl.EVP_BytesToKey(ssl.EVP_aes_256_cbc(), ssl.EVP_sha512(), chSalt, strKeyData,
            len(vKeyData), nDerivIterations, ctypes.byref(self.chKey), ctypes.byref(self.chIV))

    def SetKey(self, key):
        self.chKey = ctypes.create_string_buffer(key)

    def SetIV(self, iv):
        self.chIV = ctypes.create_string_buffer(iv)

    def Encrypt(self, data):
        buf = ctypes.create_string_buffer(len(data) + 16)
        written = ctypes.c_int(0)
        final = ctypes.c_int(0)
        ctx = ssl.EVP_CIPHER_CTX_new()
        ssl.EVP_CIPHER_CTX_init(ctx)
        ssl.EVP_EncryptInit_ex(ctx, ssl.EVP_aes_256_cbc(), None, self.chKey, self.chIV)
        ssl.EVP_EncryptUpdate(ctx, buf, ctypes.byref(written), data, len(data))
        output = buf.raw[:written.value]
        ssl.EVP_EncryptFinal_ex(ctx, buf, ctypes.byref(final))
        output += buf.raw[:final.value]
        return output

    def Decrypt(self, data):
        buf = ctypes.create_string_buffer(len(data) + 16)
        written = ctypes.c_int(0)
        final = ctypes.c_int(0)
        ctx = ssl.EVP_CIPHER_CTX_new()
        ssl.EVP_CIPHER_CTX_init(ctx)
        ssl.EVP_DecryptInit_ex(ctx, ssl.EVP_aes_256_cbc(), None, self.chKey, self.chIV)
        ssl.EVP_DecryptUpdate(ctx, buf, ctypes.byref(written), data, len(data))
        output = buf.raw[:written.value]
        ssl.EVP_DecryptFinal_ex(ctx, buf, ctypes.byref(final))
        output += buf.raw[:final.value]
        return output

try:
    if not crypter:
        from aes import *
        crypter = 'pure'
except:
    pass

class Crypter_pure(object):
    def __init__(self):
        self.m = AESModeOfOperation()
        self.cbc = self.m.modeOfOperation["CBC"]
        self.sz = self.m.aes.keySize["SIZE_256"]

    def SetKeyFromPassphrase(self, vKeyData, vSalt, nDerivIterations, nDerivationMethod):
        data = vKeyData + vSalt
        for i in range(nDerivIterations):
            data = hashlib.sha512(data).digest()
        self.SetKey(data[0:32])
        self.SetIV(data[32:32+16])
        return len(data)

    def SetKey(self, key):
        self.chKey = [ord(i) for i in key]

    def SetIV(self, iv):
        self.chIV = [ord(i) for i in iv]

    def Encrypt(self, data):
        mode, size, cypher = self.m.encrypt(data, self.cbc, self.chKey, self.sz, self.chIV)
        return ''.join(map(chr, cypher))
 
    def Decrypt(self, data):
        chData = [ord(i) for i in data]
        return self.m.decrypt(chData, self.sz, self.cbc, self.chKey, self.sz, self.chIV)

import hashlib

def Hash(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def main():

    parser = argparse.ArgumentParser(description="Bitcoin Core wallet.dat masterkey/privkey decrypter")
    
    parser.add_argument("--enc_mkey", action="store_true", default=False,
                        help="required if Master Key is Encrypted")
    parser.add_argument("mkey", action="store",
                        help="Master Key (can be encrypted or decrypted)")
    parser.add_argument("privkey", action="store",
                        help="Encrypted Private Key")
    parser.add_argument("pub", action="store",
                        help="Public Key of privkey (compressed or uncompressed)")

    
    results = parser.parse_args()
    
    if (results.enc_mkey):
        encrypted_master_key = binascii.unhexlify(results.mkey)
        encrypted_mkey, salt, method, iterations = struct.unpack_from("< 49p 9p I I", encrypted_master_key)
        
        if (debug):
            print("--------------------------------------------------------------")
            print "Successfully parsed encrypted master key\n"
            print "enc mkey: ", binascii.hexlify(encrypted_mkey)
            print "salt    : ", binascii.hexlify(salt)
            print "method  : ", method
            print "#iters  : ", iterations
            print("--------------------------------------------------------------")
        
        wallet_pass_phrase = getpass.getpass("\nEnter wallet passphrase: ")
    else:
        decrypted_master_key = binascii.unhexlify(results.mkey)
    
    enc_priv_key = binascii.unhexlify(results.privkey)
    pub_key = binascii.unhexlify(results.pub)
    
    global crypter

    if crypter == 'pycrypto':
        crypter = Crypter_pycrypto()
    elif crypter == 'ssl':
        crypter = Crypter_ssl()
        print "using ssl"
    elif crypter == 'pure':
        crypter = Crypter_pure()
        print "using slowaes"
    else:
        print("Need pycrypto of libssl or libeay32.dll or http://code.google.com/p/slowaes")
        exit(1)

    if (results.enc_mkey):
        crypter.SetKeyFromPassphrase(wallet_pass_phrase, salt, iterations, method)
        masterkey = crypter.Decrypt(encrypted_mkey)
        if (debug):
            print "Decrypted Master Key as:"
            print "dec mkey   : ", binascii.hexlify(masterkey)
            print("--------------------------------------------------------------")
    else:
        masterkey = binascii.unhexlify(results.mkey)
        
    crypter.SetKey(masterkey)
    crypter.SetIV(Hash(pub_key))
    
    d = crypter.Decrypt(enc_priv_key)
    e = crypter.Encrypt(d)

    if (debug):
        print 'dec privkey: ', binascii.hexlify(d)
        print("--------------------------------------------------------------")
    
    # Private key to public key (ecdsa transformation)
    private_key = ecdsa.SigningKey.from_string(d, curve = ecdsa.SECP256k1)
    verifying_key = private_key.get_verifying_key()
    uncomp_public_key = getPubKey(verifying_key.pubkey, False)
    if (debug):
        print 'calc pubkey: ', binascii.hexlify(uncomp_public_key)
        print 'orig pubkey: ', binascii.hexlify(pub_key)
        
    # hash sha 256 of pubkey
    sha256_1 = hashlib.sha256(uncomp_public_key)

    # hash ripemd of sha of pubkey
    ripemd160 = hashlib.new("ripemd160")
    ripemd160.update(sha256_1.digest())

    # checksum
    hashed_public_key = binascii.unhexlify("00") + ripemd160.digest()
    checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
    checksum = checksum_full[:4]
    uncomp_bin_addr = hashed_public_key + checksum

    # encode address to base58 and print
    uncomp_result_address = base58.b58encode(uncomp_bin_addr)
    if (debug):
        print "\nuncomp addr: ", uncomp_result_address
    
    network_byte_key = binascii.unhexlify("80") + d
    priv_checksum_full = hashlib.sha256(hashlib.sha256(network_byte_key).digest()).digest()
    priv_checksum = priv_checksum_full[:4]
    uncomp_full_priv = network_byte_key + priv_checksum
    
    uncomp_wif = base58.b58encode(uncomp_full_priv)
    if (debug):
        print "uncomp WIF : ", uncomp_wif        
        print("--------------------------------------------------------------")
        
    # now do compressed
    comppub_key = getPubKey(verifying_key.pubkey, True)
    if (debug):
        print 'comp pubkey: ', binascii.hexlify(comppub_key)
        print 'orig pubkey: ', binascii.hexlify(pub_key)
        
    # hash sha 256 of pubkey
    sha256_1 = hashlib.sha256(comppub_key)

    # hash ripemd of sha of pubkey
    ripemd160 = hashlib.new("ripemd160")
    ripemd160.update(sha256_1.digest())

    # checksum
    hashed_public_key = binascii.unhexlify("00") + ripemd160.digest()
    checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
    checksum = checksum_full[:4]
    comp_bin_addr = hashed_public_key + checksum

    # encode address to base58 and print
    comp_result_address = base58.b58encode(comp_bin_addr)
    if (debug): 
        print "\ncomp addr  : ", comp_result_address

    network_byte_key = binascii.unhexlify("80") + d + binascii.unhexlify("01")
    priv_checksum_full = hashlib.sha256(hashlib.sha256(network_byte_key).digest()).digest()
    priv_checksum = priv_checksum_full[:4]
    comp_full_priv = network_byte_key + priv_checksum
    
    comp_wif = base58.b58encode(comp_full_priv)
    if (debug):
        print "comp WIF   : ", comp_wif
        print("--------------------------------------------------------------")
        
    if (pub_key != comppub_key) and (pub_key != uncomp_public_key):
        print "\n\nWARNING!!!"
        print "WARNING!!! - computed public keys DO NOT match, passphrase is probably incorrect or hex data is corrupt"
        print "WARNING!!!"
        exit()
    else:
        print "\nKeys successfully decrypted:\n"
        print "decrypted mkey: ", binascii.hexlify(masterkey)
        print("--------------------------------------------------------------")
        print "uncomp addr: ", uncomp_result_address
        print "uncomp WIF : ", uncomp_wif        
        print("--------------------------------------------------------------")
        print "comp addr  : ", comp_result_address
        print "comp WIF   : ", comp_wif
        print("--------------------------------------------------------------")
        

# pywallet openssl private key implementation

def getPubKey(pubkey, compressed=False):
    # public keys are 65 bytes long (520 bits)
    # 0x04 + 32-byte X-coordinate + 32-byte Y-coordinate
    # 0x00 = point at infinity, 0x02 and 0x03 = compressed, 0x04 = uncompressed
    # compressed keys: <sign> <x> where <sign> is 0x02 if y is even and 0x03 if y is odd
    if compressed:
        if pubkey.point.y() & 1:
            key = '03' + '%064x' % pubkey.point.x()
        else:
            key = '02' + '%064x' % pubkey.point.x()
    else:
        key = '04' + \
              '%064x' % pubkey.point.x() + \
              '%064x' % pubkey.point.y()

    return key.decode('hex')

if __name__ == '__main__':
    main()