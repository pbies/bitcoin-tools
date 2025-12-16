#!/usr/bin/env python3

# pip install python-bitcoinlib

import sys

from bitcoin import SelectParams
from bitcoin.core import (
	lx,
	x,
	b2x,
	COutPoint,
	CMutableTxIn,
	CMutableTxOut,
	CMutableTransaction,
)
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress


def main():
	# ---------- CONFIG ----------
	# Choose network
	# "mainnet" for real BTC, "testnet" for testnet coins
	SelectParams("testnet")

	# UTXO you are spending (must come from a blockchain explorer / your node)
	prev_txid_hex = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"  # txid of UTXO
	prev_vout = 0  # output index in that tx

	# Amount in satoshis in that UTXO (full value)
	utxo_value_sat = 100000  # 0.001 BTC example

	# Your private key in WIF that controls the UTXO
	wif_privkey = "cVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # testnet WIF example

	# Destination address (string)
	to_address_str = "mxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # testnet P2PKH example

	# Fee in satoshis
	fee_sat = 2000

	# Optional: send all minus fee (no change)
	# If you want change, adjust this logic and add a second output.
	send_value_sat = utxo_value_sat - fee_sat
	if send_value_sat <= 0:
		print("Fee is too high or UTXO value too small", file=sys.stderr)
		sys.exit(1)

	# ---------- KEYS AND ADDRESSES ----------
	secret = CBitcoinSecret(wif_privkey)
	from_address = P2PKHBitcoinAddress.from_pubkey(secret.pub)
	to_address = P2PKHBitcoinAddress(to_address_str)

	# ---------- BUILD INPUT ----------
	prev_txid = lx(prev_txid_hex)  # little-endian
	outpoint = COutPoint(prev_txid, prev_vout)
	tx_in = CMutableTxIn(outpoint)

	# ---------- BUILD OUTPUT ----------
	tx_out = CMutableTxOut(
		send_value_sat,
		to_address.to_scriptPubKey()
	)

	# ---------- CREATE UNSIGNED TX ----------
	tx = CMutableTransaction([tx_in], [tx_out])

	# ---------- BUILD SCRIPT FOR SIGNING (scriptPubKey of the UTXO) ----------
	# Standard P2PKH: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
	script_pubkey = CScript([
		OP_DUP,
		OP_HASH160,
		from_address,
		OP_EQUALVERIFY,
		OP_CHECKSIG,
	])

	# ---------- SIGN INPUT ----------
	from bitcoin.core import Hash160, SignatureHash, SIGHASH_ALL
	sighash = SignatureHash(script_pubkey, tx, 0, SIGHASH_ALL)

	signature = secret.sign(sighash) + bytes([SIGHASH_ALL])
	pubkey = secret.pub

	tx_in.scriptSig = CScript([signature, pubkey])

	# ---------- SERIALIZE ----------
	raw_tx = tx.serialize()
	raw_tx_hex = b2x(raw_tx)

	print("Raw transaction hex:")
	print(raw_tx_hex)


if __name__ == "__main__":
	main()
