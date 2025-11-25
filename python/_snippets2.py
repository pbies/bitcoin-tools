def b58encode(b: bytes) -> str:
	n = int.from_bytes(b, "big")
	out = bytearray()
	while n > 0:
		n, r = divmod(n, 58)
		out.append(_ALPHABET[r])
	for c in b:
		if c == 0:
			out.append(_ALPHABET[0])
		else:
			break
	out.reverse()
	return out.decode()

def ripemd160(x: bytes) -> bytes:
	h = hashlib.new("ripemd160")
	h.update(x)
	return h.digest()

def sha256(x: bytes) -> bytes:
	return hashlib.sha256(x).digest()

def pubkey_from_priv_int(priv_int: int, compressed: bool = True) -> bytes:
	priv = priv_int.to_bytes(32, "big")
	sk = ecdsa.SigningKey.from_string(priv, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	px = vk.pubkey.point.x()
	py = vk.pubkey.point.y()
	x = int(px).to_bytes(32, "big")
	y = int(py).to_bytes(32, "big")
	if compressed:
		prefix = b'\x02' if (py % 2 == 0) else b'\x03'
		return prefix + x
	else:
		return b'\x04' + x + y

def pubkey_to_p2pkh_address(pubkey_bytes: bytes, mainnet: bool = True) -> str:
	h160 = ripemd160(sha256(pubkey_bytes))
	prefix = b'\x00' if mainnet else b'\x6f'
	payload = prefix + h160
	check = sha256(sha256(payload))[:4]
	return b58encode(payload + check)

def wif_from_priv_int(priv_int: int, compressed: bool = True, mainnet: bool = True) -> str:
	priv = priv_int.to_bytes(32, "big")
	prefix = b'\x80' if mainnet else b'\xef'
	payload = prefix + priv
	if compressed:
		payload += b'\x01'
	check = sha256(sha256(payload))[:4]
	return b58encode(payload + check)
