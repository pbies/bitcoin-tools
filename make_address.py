#!/usr/bin/env python3
# make_address.py v2022.12.27 (https://bitcointalk.org/index.php?topic=5432111)
from typing import List, Tuple, Callable
from functools import reduce
import secrets
import sys
show_testnet: bool = False
show_p2pkh_uncompressed: bool = True
show_p2pkh_compressed: bool = True
show_p2wpkh: bool = True
secp256k1_field_order: int = 2**256 - 0x1000003d1
secp256k1_group_order: int = 2**256 - 0x14551231950b75fc4402da1732fc9bebf
secp256k1_generator: Tuple[int, int] = (0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798, 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
u32: int = 0xffffffff
def fail_if(result: bool, message: str) -> None:
    if result:
        sys.exit('fatal error: ' + message)
def rotl32(x: int, s: int) -> int:
    # https://en.wikipedia.org/wiki/Circular_shift
    return (x << s | x >> (32 - s)) & u32
def ripemd160(x: bytes) -> bytes:
    # https://cacr.uwaterloo.ca/hac/about/chap9.pdf (algorithm 9.55, page 350) ['H1' -> 'h0', 'X' -> 'w']
    # this took some effort to derive from the above reference, I first implemented MD4 (from the same reference; algorithm 9.49, page 346) and then manipulated that into RIPEMD-160.
    yl: List[int] = [0] * 16 + [0x5a827999] * 16 + [0x6ed9eba1] * 16 + [0x8f1bbcdc] * 16 + [0xa953fd4e] * 16
    yr: List[int] = [0x50a28be6] * 16 + [0x5c4dd124] * 16 + [0x6d703ef3] * 16 + [0x7a6d76e9] * 16 + [0] * 16
    zl: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] + [7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8] + [3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12] + [1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2] + [4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13]
    zr: List[int] = [5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12] + [6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2] + [15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13] + [8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14] + [12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11]
    sl: List[int] = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8] + [7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12] + [11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5] + [11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12] + [9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6]
    sr: List[int] = [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6] + [9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11] + [9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5] + [15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8] + [8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11]
    fx: List[Callable[[int, int, int], int]] = [lambda u, v, w: u ^ v ^ w] * 16 + [lambda u, v, w: (u & v) | (~u & w)] * 16 + [lambda u, v, w: (u | ~v) ^ w] * 16 + [lambda u, v, w: (u & w) | (v & ~w)] * 16 + [lambda u, v, w: u ^ (v | ~w)] * 16
    padded: bytes = x + b'\x80' + b'\x00' * (64 - (len(x)+1+8) % 64) + (len(x) * 8).to_bytes(8, 'little')
    h0, h1, h2, h3, h4 = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0
    for block_index in range(len(padded) // 64):
        block: bytes = padded[block_index*64:block_index*64+64]
        w: List[int] = [int.from_bytes(block[i*4:i*4+4], 'little') for i in range(16)]
        al, bl, cl, dl, el = h0, h1, h2, h3, h4
        ar, br, cr, dr, er = h0, h1, h2, h3, h4
        for j in range(80):
            tl = al + fx[j](bl, cl, dl) + w[zl[j]] + yl[j]
            tr = ar + fx[79-j](br, cr, dr) + w[zr[j]] + yr[j]
            al, bl, cl, dl, el = el, (el + rotl32(tl & u32, sl[j])) & u32, bl, rotl32(cl, 10), dl
            ar, br, cr, dr, er = er, (er + rotl32(tr & u32, sr[j])) & u32, br, rotl32(cr, 10), dr
        h0, h1, h2, h3, h4 = (h1 + cl + dr) & u32, (h2 + dl + er) & u32, (h3 + el + ar) & u32, (h4 + al + br) & u32, (h0 + bl + cr) & u32
    return h0.to_bytes(4, 'little') + h1.to_bytes(4, 'little') + h2.to_bytes(4, 'little') + h3.to_bytes(4, 'little') + h4.to_bytes(4, 'little')
def sha256(x: bytes) -> bytes:
    # https://en.wikipedia.org/wiki/SHA-2#Pseudocode
    # one thing that might catch (compared to the reference) is that I've replaced right rotations with left ones.
    k: List[int] = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
    padded: bytes = x + b'\x80' + b'\x00' * (64 - (len(x)+1+8) % 64) + (len(x) * 8).to_bytes(8, 'big')
    h0, h1, h2, h3, h4, h5, h6, h7 = 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    for block_index in range(len(padded) // 64):
        block: bytes = padded[block_index*64:block_index*64+64]
        w: List[int] = [int.from_bytes(block[i*4:i*4+4], 'big') for i in range(16)] + [0] * 48
        for i in range(16, 64):
            s0: int = rotl32(w[i-15], 25) ^ rotl32(w[i-15], 14) ^ (w[i-15] >> 3)
            s1: int = rotl32(w[i-2], 15) ^ rotl32(w[i-2], 13) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & u32
        a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
        for i in range(64):
            t1: int = (rotl32(e, 26) ^ rotl32(e, 21) ^ rotl32(e, 7)) + ((e & f) ^ (~e & g)) + h + w[i] + k[i]
            t2: int = (rotl32(a, 30) ^ rotl32(a, 19) ^ rotl32(a, 10)) + ((a & b) ^ (a & c) ^ (b & c))
            a, b, c, d, e, f, g, h = (t1 + t2) & u32, a, b, c, (d + t1) & u32, e, f, g
        h0, h1, h2, h3, h4, h5, h6, h7 = (h0 + a) & u32, (h1 + b) & u32, (h2 + c) & u32, (h3 + d) & u32, (h4 + e) & u32, (h5 + f) & u32, (h6 + g) & u32, (h7 + h) & u32
    return h0.to_bytes(4, 'big') + h1.to_bytes(4, 'big') + h2.to_bytes(4, 'big') + h3.to_bytes(4, 'big') + h4.to_bytes(4, 'big') + h5.to_bytes(4, 'big') + h6.to_bytes(4, 'big') + h7.to_bytes(4, 'big')
def rcp(x: int) -> int:
    # https://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Using_Euler's_theorem
    # on 3.8+, use the much faster built-in modular inverse (exponent -1), otherwise use Euler's theorem.
    return pow(x, -1 if sys.hexversion >= 0x030800f0 else secp256k1_field_order-2, secp256k1_field_order)
def is_on_curve(point: Tuple[int, int]) -> bool:
    fail_if(point[0] < 0 or point[0] >= secp256k1_field_order, 'x component is out of range.')
    fail_if(point[1] < 0 or point[1] >= secp256k1_field_order, 'y component is out of range.')
    return (point[1]**2 - point[0]**3) % secp256k1_field_order == 7
def add(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    # https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_addition
    # https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_doubling
    fail_if(not is_on_curve(a) and a != (0, 0), 'point is neither on the curve nor the identity point.')
    fail_if(not is_on_curve(b) and b != (0, 0), 'point is neither on the curve nor the identity point.')
    if b == (0, 0):
        return a
    if a == (0, 0):
        return b
    if b == (a[0], secp256k1_field_order - a[1]):
        return (0, 0)
    slope: int = (a[1] - b[1]) * rcp(a[0] - b[0]) if a != b else 3 * a[0]**2 * rcp(2 * a[1])
    x: int = slope**2 - a[0] - b[0]
    y: int = slope * (a[0] - x) - a[1]
    return (x % secp256k1_field_order, y % secp256k1_field_order)
def scale(point: Tuple[int, int], scalar: int) -> Tuple[int, int]:
    # https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add
    fail_if(not is_on_curve(point), 'point is not on the curve.')
    fail_if(scalar < 1 or scalar >= secp256k1_group_order, 'scalar is out of range.')
    return point if scalar == 1 else add(scale(add(point, point), scalar // 2), (0, 0) if scalar % 2 == 0 else point)
def rebase_bytes(x: bytes, *, base: int, min_length: int = 0) -> List[int]:
    # this construction shows up in both base58 and bech32.
    value: int = int.from_bytes(x, 'big')
    result: List[int] = []
    while value != 0:
        value, remainder = divmod(value, base)
        result.append(remainder)
    return [0] * (min_length - len(result)) + result[::-1]
def base58_encode(x: bytes) -> str:
    # https://en.bitcoin.it/wiki/Base58Check_encoding
    return '1' * (len(x) - len(x.lstrip(b'\x00'))) + ''.join('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'[v] for v in rebase_bytes(x, base=58))
def wif_from_scalar(scalar: int, *, uncompressed: bool = False, testnet: bool = False) -> str:
    # https://en.bitcoin.it/wiki/Wallet_import_format
    fail_if(scalar < 1 or scalar >= secp256k1_group_order, 'scalar is out of range.')
    version: bytes = b'\xef' if testnet else b'\x80'
    payload: bytes = scalar.to_bytes(32, 'big') + (b'' if uncompressed else b'\x01')
    return base58_encode(version + payload + sha256(sha256(version + payload))[:4])
def p2pkh_from_point(point: Tuple[int, int], *, uncompressed: bool = False, testnet: bool = False) -> str:
    # https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses
    # https://en.bitcoin.it/wiki/List_of_address_prefixes
    fail_if(not is_on_curve(point), 'point is not on the curve.')
    version: bytes = b'\x6f' if testnet else b'\x00'
    bytes_x: bytes = point[0].to_bytes(32, 'big')
    maybe_bytes_y: bytes = point[1].to_bytes(32, 'big') if uncompressed else b''
    prefix: bytes = b'\x04' if uncompressed else (b'\x02' if point[1] % 2 == 0 else b'\x03')
    payload: bytes = ripemd160(sha256(prefix + bytes_x + maybe_bytes_y))
    return base58_encode(version + payload + sha256(sha256(version + payload))[:4])
def bech32_checksum(x: List[int], *, testnet: bool = False) -> List[int]:
    # https://en.bitcoin.it/wiki/BIP_0173
    # this formulation bears little resemblance to the reference, but it fits my way of thinking better.
    expanded: List[int] = ([3, 3, 0, 20, 2] if testnet else [3, 3, 0, 2, 3]) + x + [0, 0, 0, 0, 0, 0]
    code: int = 1 ^ reduce(lambda a, b: (0x3b6a57b2 if a & (1 << 25) else 0) ^ (0x26508e6d if a & (1 << 26) else 0) ^ (0x1ea119fa if a & (1 << 27) else 0) ^ (0x3d4233dd if a & (1 << 28) else 0) ^ (0x2a1462b3 if a & (1 << 29) else 0) ^ ((a << 5 | b) & 0x3fffffff), expanded, 1)
    return [code >> 25, code >> 20 & 31, code >> 15 & 31, code >> 10 & 31, code >> 5 & 31, code & 31]
def bech32_encode(x: List[int]) -> str:
    # https://en.bitcoin.it/wiki/BIP_0173
    return ''.join('qpzry9x8gf2tvdw0s3jn54khce6mua7l'[v] for v in x)
def p2wpkh_from_point(point: Tuple[int, int], *, testnet: bool = False) -> str:
    # https://en.bitcoin.it/wiki/BIP_0173
    fail_if(not is_on_curve(point), 'point is not on the curve.')
    bytes_x: bytes = point[0].to_bytes(32, 'big')
    version: List[int] = [0]
    payload: List[int] = rebase_bytes(ripemd160(sha256((b'\x02' if point[1] % 2 == 0 else b'\x03') + bytes_x)), base=32, min_length=32)
    return ('tb' if testnet else 'bc') + '1' + bech32_encode(version + payload + bech32_checksum(version + payload, testnet=testnet))
def show_info(point: Tuple[int, int], scalar: int, *, p2pkh: bool = False, uncompressed: bool = False, testnet: bool = False) -> None:
    fail_if(not p2pkh and uncompressed, 'p2wpkh addresses are always compressed.')
    kind: str = ('Legacy' if p2pkh else 'Native SegWit') + ((', Uncompressed' if uncompressed else ', Compressed') if p2pkh else '') + (', Testnet' if testnet else '')
    address: str = p2pkh_from_point(point, uncompressed=uncompressed, testnet=testnet) if p2pkh else p2wpkh_from_point(point, testnet=testnet)
    private_key: str = (('' if uncompressed else 'p2pkh:') if p2pkh else 'p2wpkh:') + wif_from_scalar(scalar, uncompressed=uncompressed, testnet=testnet)
    print('       +------+' + '-' * len(kind) + '--+\n' + '       | Type | ' + kind + ' |\n    +--+------+' + '-' * len(kind) + '--+' + '-' * (len(address) - len(kind) - 1) + '+\n    | Address | ' + address + ' |\n+---+---------+' + '-' * len(address) + '--+' + '-' * (len(private_key) - len(address) - 1) + '+\n| Private Key | ' + private_key + ' |\n+-------------+' + '-' * len(private_key) + '--+')
def self_test() -> bool:
    # this function generates a test pattern consisting of 96 different addresses and 64 different WIFs, and then hashes the result to confirm its correctness.
    # the test pattern is slid 9170 places to slightly increase defect coverage (that offset includes some edge cases; ask me about it on Bitcointalk, if you're interested).
    pattern: str = ''
    for i in range(9171, 9171+16):
        scalar: int = (i * 0x9e3779b97f4a7c15f39cc0605cedc833477394a4b665b1d25e46d78ce158d565) % secp256k1_group_order
        point: Tuple[int, int] = scale(secp256k1_generator, scalar)
        pattern += wif_from_scalar(scalar, uncompressed=True, testnet=True) + wif_from_scalar(scalar, testnet=True) + wif_from_scalar(scalar, uncompressed=True) + wif_from_scalar(scalar)
        pattern += p2pkh_from_point(point, uncompressed=True, testnet=True) + p2pkh_from_point(point, testnet=True) + p2pkh_from_point(point, uncompressed=True) + p2pkh_from_point(point)
        pattern += p2wpkh_from_point(point, testnet=True) + p2wpkh_from_point(point)
    return base58_encode(ripemd160(pattern.encode('ascii'))) == '4RH6F51YXGjTEn5jnvxvFjmsN86j'
def main(args: List[str]) -> None:
    fail_if(len(args) not in { 0, 1 }, 'expected zero or one argument(s).')
    fail_if(len(args) == 1 and (len(args[0]) < 3 or args[0][:2].lower() != '0x' or any(c not in '0123456789abcdef' for c in args[0][2:].lower())), 'expected a private key in hexadecimal form.')
    fail_if(not self_test(), 'self-test failed.')
    scalar: int = secrets.randbits(256) if len(args) == 0 else int(args[0], 16)
    point: Tuple[int, int] = scale(secp256k1_generator, scalar)
    if show_p2pkh_uncompressed:
        show_info(point, scalar, p2pkh=True, uncompressed=True, testnet=show_testnet)
    if show_p2pkh_compressed:
        show_info(point, scalar, p2pkh=True, testnet=show_testnet)
    if show_p2wpkh:
        show_info(point, scalar, testnet=show_testnet)
if __name__ == '__main__':
    main(sys.argv[1:])
