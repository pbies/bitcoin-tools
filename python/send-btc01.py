#!/usr/bin/env python3

# pip3 install bitcoinlib

from bitcoinlib.services import ElectrumService
from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key

# Replace with your WIF private key
wif_private_key = "YOUR_PRIVATE_KEY_IN_WIF_FORMAT"

# Create a Key object from the WIF
private_key = Key(wif_private_key)

# Electrum server URL (you can use a public one or your own)
electrum_server = "ssl://electrum.xays.org:50002"

# Create an Electrum service for broadcasting
service = ElectrumService(url=electrum_server)

# Recipient address
recipient_address = "RECIPIENT_ADDRESS"

# Amount to send (in BTC)
amount = 0.001  # 0.001 BTC

# Optional fee per KB (suggested by the network)
fee_rate = None  # Use None to let the library calculate

# Build the transaction
tx = Transaction(outputs=[(recipient_address, amount)])

# Sign the transaction with the private key
signed_tx = tx.sign(private_key, fee_rate=fee_rate)

# Broadcast the transaction
tx_hash = service.send_transaction(signed_tx)

print(f"Transaction sent! Hash: {tx_hash}")
