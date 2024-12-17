#!/usr/bin/env python3

import json
import sys
from bsddb3 import db

def load_wallet(file_path):
    try:
        wallet_db = db.DB()
        wallet_db.open(file_path, 'main', db.DB_BTREE, db.DB_RDONLY)
        cursor = wallet_db.cursor()
        data = {}

        while True:
            record = cursor.next()
            if record is None:
                break

            key, value = record

            # Filter out irrelevant entries (heuristic filtering)
            if len(key) < 4 or len(value) < 4:
                continue  # Skip very short keys/values

            # Decode relevant data to hex
            data[key.hex()] = value.hex()

        cursor.close()
        wallet_db.close()
        return data
    except Exception as e:
        print(f"Failed to load wallet file: {e}")
        sys.exit(1)

def categorize_wallet_data(wallet_data):
    categorized = {
        "addresses": [],
        "keys": [],
        "transactions": [],
        "metadata": []
    }

    for key, value in wallet_data.items():
        if key.startswith("30") or key.startswith("32"):  # Example: Address-like keys
            categorized["addresses"].append({"key": key, "value": value})
        elif key.startswith("2b") or key.startswith("2c"):  # Example: Private keys
            categorized["keys"].append({"key": key, "value": value})
        elif key.startswith("01"):  # Example: Transactions
            categorized["transactions"].append({"key": key, "value": value})
        else:
            categorized["metadata"].append({"key": key, "value": value})

    return categorized

def dump_wallet(file_path):
    wallet_data = load_wallet(file_path)
    categorized_data = categorize_wallet_data(wallet_data)

    wallet_data_hex = json.dumps(wallet_data, indent=4).encode("utf-8").hex()

    return {
        "hex": wallet_data_hex,
        "categorized": categorized_data
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dump_wallet.py <wallet_file_path>")
        sys.exit(1)

    wallet_file_path = sys.argv[1]
    dumped_wallet = dump_wallet(wallet_file_path)

    o = open(sys.argv[1]+'.json', 'w')

    #print("\n--- Categorized Wallet Data ---")
    o.write(json.dumps(dumped_wallet["categorized"], indent=4))
    o.flush()

    print('\a', end='', file=sys.stderr)
