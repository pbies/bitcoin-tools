#!/usr/bin/env python3

import hashlib
import struct
import binascii

def create_raw_transaction(prev_txid, prev_output_index, recipient_address, amount):
    raw_tx = b""

    # Transaction version
    raw_tx += struct.pack("<L", 1)  # 4 bytes little-endian

    # Number of inputs
    raw_tx += struct.pack("B", 1)    # 1 byte

    # Input details
    raw_tx += binascii.unhexlify(prev_txid)[::-1]  # Convert txid to little-endian
    raw_tx += struct.pack("<L", prev_output_index)  # 4 bytes little-endian

    # Input script size
    raw_tx += struct.pack("B", 0)  # 1 byte

    # Sequence number
    raw_tx += binascii.unhexlify("ffffffff")  # 4 bytes

    # Number of outputs
    raw_tx += struct.pack("B", 1)  # 1 byte

    # Output details
    output_amount = int(amount * 100000000)  # Convert to satoshis
    raw_tx += struct.pack("<Q", output_amount)  # 8 bytes little-endian

    # Output script size
    raw_tx += struct.pack("B", 25)  # P2PK output script size

    # Output script (P2PK)
    raw_tx += binascii.unhexlify("41")  # Push 65 bytes to stack
    raw_tx += binascii.unhexlify(recipient_address)

    # Locktime
    raw_tx += binascii.unhexlify("00000000")  # 4 bytes

    return raw_tx

for l in open('p2pk10.txt'):
# Define inputs 64 hex chars
    ar=l.split(',')
    prev_txid = ar[1]
    prev_output_index = 0

# Define recipient address 130 hex chars
    recipient_address = "04dbc0249573c19545ffca4b65f3eb2117fc0effa133ac003b6191ffc1b87df97eaca9cc164649a1d1ded9a268ae76b9be782c2c7b3a1053a0e7627d93c87365a8"

# Define amount to send
    amount = 1.0

# Create the raw transaction
    raw_transaction = create_raw_transaction(prev_txid, prev_output_index, recipient_address, amount)

    print(binascii.hexlify(raw_transaction).decode('ascii')+'\n')

# pvk hex e57b6dc4397eebce24562dda4ae02d5179e0c24363152d5f410fbd40671a9562
# pvk wif 5KZMPrbnCnB3FsFuwPWjCQWcCV8u5EVC7upjpdbeW7anhbESzcc
# p2pkh 04dbc0249573c19545ffca4b65f3eb2117fc0effa133ac003b6191ffc1b87df97eaca9cc164649a1d1ded9a268ae76b9be782c2c7b3a1053a0e7627d93c87365a8
# rawtx 01000000010002b3e4ea557d18b360b673e867d08da2e18643b1bb60b351d482a150b04ef10000000000ffffffff0100e1f50500000000194104dbc0249573c19545ffca4b65f3eb2117fc0effa133ac003b6191ffc1b87df97eaca9cc164649a1d1ded9a268ae76b9be782c2c7b3a1053a0e7627d93c87365a800000000
