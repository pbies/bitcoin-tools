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

def systype():
	if platform.system() == "Darwin":
		return 'Mac'
	elif platform.system() == "Windows":
		return 'Win'
	return 'Linux'

def inverse_mod( a, m ):
	if a < 0 or m <= a: a = a % m
	c, d = a, m
	uc, vc, ud, vd = 1, 0, 0, 1
	while c != 0:
		q, c, d = divmod( d, c ) + ( c, )
		uc, vc, ud, vd = ud - q*uc, vd - q*vc, uc, vc
	assert d == 1
	if ud > 0: return ud
	else: return ud + m

def hash_160(public_key):
	md = hashlib.new('ripemd160')
	md.update(hashlib.sha256(public_key).digest())
	return md.digest()

def b58encode(v):
	""" encode v, which is a string of bytes, to base58.
	"""

	long_value = 0
	for (i, c) in enumerate(v[::-1]):
		long_value += (256**i) * c

	result = ''
	while long_value >= __b58base:
		div, mod = divmod(long_value, __b58base)
		result = __b58chars[mod] + result
		long_value = div
	result = __b58chars[long_value] + result

	# Bitcoin does a little leading-zero-compression:
	# leading 0-bytes in the input become leading-1s
	nPad = 0
	for c in v:
		if c == 0: nPad += 1
		else: break

	return (__b58chars[0]*nPad) + result

def b58decode(v, length):
	""" decode v into a string of len bytes
	"""
	long_value = 0
	for (i, c) in enumerate(v[::-1]):
		long_value += __b58chars.find(c) * (__b58base**i)

	result = b''
	while long_value >= 256:
		div, mod = divmod(long_value, 256)
		result = bytes([mod]) + result
		long_value = div
	result = bytes([long_value]) + result

	nPad = 0
	for c in v:
		if c == __b58chars[0]: nPad += 1
		else: break

	result = bytes([0])*nPad + result
	if length is not None and len(result) != length:
		return None

	return result

def EncodeBase58Check(secret):
	hash_val = Hash(secret)
	return b58encode(secret + hash_val[0:4])

def DecodeBase58Check(sec):
	vchRet = b58decode(sec, None)
	secret = vchRet[0:-4]
	csum = vchRet[-4:]
	hash_val = Hash(secret)
	cs32 = hash_val[0:4]
	if cs32 != csum:
		return None
	else:
		return secret

def one_element_in(a, string):
	for i in a:
		if i in string:
			return True
	return False

def read_jsonfile(filename):
	with open(filename, 'r') as filin:
		txdump = filin.read()
	return json.loads(txdump)

def write_jsonfile(filename, array):
	with open(filename, 'w') as filout:
		filout.write(json.dumps(array, sort_keys=True, indent=0))
