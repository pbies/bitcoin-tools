#!/usr/bin/env python3

def hex_to_b58c(h):
	return base58.b58encode_check(bytes.fromhex(h)).decode()

def int_to_b58c_wif(b):
	return base58.b58encode_check(b'\x80'+b.to_bytes(32,'big')).decode()

def int_to_bytes3(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def getWif(privkey):
	wif = b"\x80" + privkey
	wif = b58(wif + sha256(sha256(wif))[:4])
	return wif

def b58(data):
	B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
	if data[0] == 0:
		return "1" + b58(data[1:])
	x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
	ret = ""
	while x > 0:
		ret = B58[x % 58] + ret
		x = x // 58
	return ret

def sha256(data):
	digest = hashlib.new("sha256")
	digest.update(data)
	return digest.digest()

def bytes_to_int(k):
	return int.from_bytes(k,'big')

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def int_to_bytes4(number, length):
	return number.to_bytes(length,'big')

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

# pubkey compress to uncompress

import binascii

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def decompress_pubkey(pk):
	x = int.from_bytes(pk[1:33], byteorder='big')
	y_sq = (pow(x, 3, p) + 7) % p
	y = pow(y_sq, (p + 1) // 4, p)
	if y % 2 != pk[0] % 2:
		y = p - y
	y = y.to_bytes(32, byteorder='big')
	return b'\x04' + pk[1:33] + y

with open('add.txt') as f:
	for line in f:
		line=line.strip()
		print(binascii.hexlify(decompress_pubkey(binascii.unhexlify(line))).decode(),file=open("uncomp.txt", "a"))

# pubkey uncompress to compress

def cpub(x,y):
	prefix = '02' if y % 2 == 0 else '03'
	c = prefix+ hex(x)[2:].zfill(64)
	return c
with open('add.txt') as f:
	for line in f:
		line=line.strip()
		x = int(line[2:66], 16)
		y = int(line[66:], 16)
		pub04=cpub(x,y)

		print(pub04,file=open("comp.txt", "a"))

def sha256(data):
	return hashlib.sha256(data).digest()

def ripemd160(x):
	return hashlib.new("ripemd160").update(x).digest()

def generate_random_private_key() -> str:
	return hex(random.getrandbits(256))[2:].zfill(64)

def pvk_to_pubkey(h):
	sk = ecdsa.SigningKey.from_string(bytes.fromhex(h), curve=ecdsa.SECP256k1)
	vk = sk.verifying_key
	return (b'\04' + sk.verifying_key.to_string()).hex()

def wif_to_private_key(wif):
	decoded = base58.b58decode_check(wif)
	return decoded[1:] # Remove 0x80 prefix

def private_key_to_address(private_key_bytes):
	sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	pub_key = b'\x04' + vk.to_string()

	sha256_1 = hashlib.sha256(pub_key).digest()
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(sha256_1)
	hashed_pubkey = ripemd160.digest()

	mainnet_pubkey = b'\x00' + hashed_pubkey
	checksum = hashlib.sha256(hashlib.sha256(mainnet_pubkey).digest()).digest()[:4]
	binary_address = mainnet_pubkey + checksum
	address = base58.b58encode(binary_address)
	return address.decode()

def generate_random_private_key1() -> str:
	return hex(random.getrandbits(256))[2:].zfill(64)

def generate_random_private_key2() -> str:
	return os.urandom(32).hex().zfill(64)

def generate_random_private_key3() -> str:
	return hex(random.randint(1,0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140))[2:].zfill(64)

def generate_random_private_key4() -> str:
	return secrets.token_hex(32)

def sha256(data):
	return hashlib.sha256(data).digest()

def ripemd160(data):
	h = hashlib.new('ripemd160')
	h.update(data)
	return h.digest()

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open('log.txt', 'a') as log_file:
		log_file.write(f'{timestamp} {message}\n')
	print(f'{timestamp} {message}', flush=True)

# btree start

class Node:
	def __init__(self, data):
		self.left = None
		self.right = None
		self.data = data

	def insert(self, data):
		if self.data:
			if data < self.data:
				if self.left is None:
					self.left = Node(data)
				else:
					self.left.insert(data)
			elif data > self.data:
					if self.right is None:
						self.right = Node(data)
					else:
						self.right.insert(data)
		else:
			self.data = data

def buildTree(addrs, start, end):
	if (start > end):
		return None

	mid = int(start + (end - start) / 2)
	node = Node(addrs[mid])

	node.left = buildTree(addrs, start, mid - 1)
	node.right = buildTree(addrs, mid + 1, end)

	return node

def search(root, key):
	if root is None or root.data == key:
		return root

	if root.data < key:
		return search(root.right, key)

	return search(root.left, key)

tree = buildTree(pubkeys, 0, len(pubkeys) - 1)

if pubkey and search(tree, pubkey):
	pass

# btree stop
