#!/usr/bin/env python3

DEFAULT_BECH32_HRP = "cro"
path   = "m/44'/0'/0'/0/0"

def privkey_to_pubkey(privkey: bytes) -> bytes:
	privkey_obj = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
	pubkey_obj = privkey_obj.get_verifying_key()
	return pubkey_obj.to_string("compressed")

def pubkey_to_address(pubkey: bytes, *, hrp: str = DEFAULT_BECH32_HRP) -> str:
	s = hashlib.new("sha256", pubkey).digest()
	r = hashlib.new("ripemd160", s).digest()
	five_bit_r = bech32.convertbits(r, 8, 5)
	assert five_bit_r is not None, "Unsuccessful bech32.convertbits call"
	return bech32.bech32_encode(hrp, five_bit_r)

def privkey_to_address(privkey: bytes, *, hrp: str = DEFAULT_BECH32_HRP) -> str:
	pubkey = privkey_to_pubkey(privkey)
	return pubkey_to_address(pubkey, hrp=hrp)

def pvk_to_wif(z):
	private_key_static = z
	extended_key = "80"+private_key_static
	first_sha256 = hashlib.sha256(binascii.unhexlify(extended_key)).hexdigest()
	second_sha256 = hashlib.sha256(binascii.unhexlify(first_sha256)).hexdigest()
	final_key = extended_key+second_sha256[:8]
	return base58.b58encode(binascii.unhexlify(final_key))

def lines(f):
	return sum(1 for line in open(f))
