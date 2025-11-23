from web3 import Web3
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
RPC = os.getenv('RPC_URL')
PK = os.getenv('PRIVATE_KEY')
if not RPC:
    raise RuntimeError("Missing RPC_URL in .env")
w3 = Web3(Web3.HTTPProvider(RPC))
print("Connected:", w3.is_connected())
print("Chain ID:", w3.eth.chain_id)
if PK:
    acct = w3.eth.account.from_key(PK)
    bal = w3.eth.get_balance(acct.address)
    print("Address:", acct.address)
    print("Balance (wei):", bal)
    print("Balance (ETH):", w3.from_wei(bal, "ether"))
