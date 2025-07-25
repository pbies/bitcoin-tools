#!/usr/bin/env python3

from web3 import Web3
from eth_account import Account
from multiprocessing import Pool, Lock, Manager
from tqdm import tqdm
import time

# === Settings ===
alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'
web3 = Web3(Web3.HTTPProvider(alchemy_url))

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    }
]

# Replace with the contract address of the token you want to scan
TOKEN_CONTRACTS = {
	"USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
	"USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
	"SHIBA": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
}

def scan_token_balances(private_key: str):
	acct = Account.from_key(private_key)
	address = acct.address
	print(f"Checking address: {address}")

	for name, contract_address in TOKEN_CONTRACTS.items():
		token_contract = web3.eth.contract(address=contract_address, abi=ERC20_ABI)
		try:
			balance = token_contract.functions.balanceOf(address).call()
			decimals = token_contract.functions.decimals().call()
			symbol = token_contract.functions.symbol().call()
			adjusted_balance = balance / (10 ** decimals)
			if adjusted_balance > 0:
				print(f"  {symbol}: {adjusted_balance}")
		except Exception as e:
			print(f"  Error checking {name}: {e}")

raw=open('input.txt','r').read().splitlines()

for key in raw:
	scan_token_balances(key)
