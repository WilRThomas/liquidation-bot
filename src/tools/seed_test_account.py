from web3 import Web3
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sdk.clients import get_w3


"""
Flow:
1. Load RPC URL, liquidator address, borrower address and funding private key from .env.
2. Connect to the fork with Web3.
3. Use the funding account (which has a lot of ETH on Anvil) to:
   - call WETH.deposit() with some ETH to mint WETH
   - transfer that WETH to the liquidator address and borrower address
4. Print final WETH balances for both accounts.
"""

# Load .env from project root (two levels up from this file: src/tools -> src -> project)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# --- Environment variables ---

RPC = os.getenv("RPC_URL")
LIQ_RAW = os.getenv("LIQUIDATOR_ADDRESS")
BORROWER1_RAW = os.getenv("BORROWER_1")
FUND_PK = os.getenv("FUNDING_PRIVATE_KEY")
LIQ_WETH_TARGET = os.getenv("LIQ_WETH_TARGET", "1000")
BORROWER_WETH_TARGET = os.getenv("BORROWER_WETH_TARGET", "200")

if not RPC:
    raise RuntimeError("RPC_URL is not set in .env")

if not LIQ_RAW:
    raise RuntimeError("LIQUIDATOR_ADDRESS is not set in .env")

if not BORROWER1_RAW:
    raise RuntimeError("BORROWER_1 is not set in .env")

if not FUND_PK:
    raise RuntimeError("FUNDING_PRIVATE_KEY is not set in .env")

# --- Web3 setup ---

w3 = get_w3()

if not w3.is_connected():
    raise RuntimeError(f"Could not connect to RPC at {RPC}")

LIQ = Web3.to_checksum_address(LIQ_RAW)
BORROWER1 = Web3.to_checksum_address(BORROWER1_RAW)
fund_acct = w3.eth.account.from_key(FUND_PK)

liq_target_wei = w3.to_wei(int(LIQ_WETH_TARGET), "ether")
bor1_target_wei = w3.to_wei(int(BORROWER_WETH_TARGET), "ether")

# --- WETH address + minimal ABI ---

WETH = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2")

weth_abi = [
    {
        "name": "deposit",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [],
        "outputs": [],
    },
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "transfer",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
]

weth = w3.eth.contract(address=WETH, abi=weth_abi)

def weth_balance(addr: str) -> int:
    return weth.functions.balanceOf(addr).call()


def mint_weth_to(recipient: str, amount_wei: int) -> None:
    """Wrap ETH into WETH in the funding account, then send to `recipient`."""
    print("Funding account:", fund_acct.address)
    print("Recipient:", recipient)

    # 1) Wrap ETH into WETH in the funding account
    nonce = w3.eth.get_transaction_count(fund_acct.address)
    tx1 = weth.functions.deposit().build_transaction(
        {
            "from": fund_acct.address,
            "value": amount_wei,
            "nonce": nonce,
            "gas": 200_000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed1 = w3.eth.account.sign_transaction(tx1, private_key=FUND_PK)
    tx_hash1 = w3.eth.send_raw_transaction(signed1.raw_transaction)
    receipt1 = w3.eth.wait_for_transaction_receipt(tx_hash1)
    print("WETH deposit tx:", tx_hash1.hex())
    print("WETH deposit status:", receipt1.status)

    # 2) Transfer that WETH from funding account to the recipient
    tx2 = weth.functions.transfer(recipient, amount_wei).build_transaction(
        {
            "from": fund_acct.address,
            "nonce": w3.eth.get_transaction_count(fund_acct.address),
            "gas": 200_000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed2 = w3.eth.account.sign_transaction(tx2, private_key=FUND_PK)
    tx_hash2 = w3.eth.send_raw_transaction(signed2.raw_transaction)
    receipt2 = w3.eth.wait_for_transaction_receipt(tx_hash2)
    print("WETH transfer tx:", tx_hash2.hex())
    print("WETH transfer status:", receipt2.status)


def main() -> None:
    print("Connected to:", RPC)
    print("Chain ID:", w3.eth.chain_id)
    print("Block:", w3.eth.block_number)

    liq_curr = weth_balance(LIQ)
    bor1_curr = weth_balance(BORROWER1)

    liq_topup = max(liq_target_wei - liq_curr, 0)
    bor1_topup = max(bor1_target_wei - bor1_curr, 0)

    if liq_topup > 0:
        print(f"Top-up liquidator by {w3.from_wei(liq_topup, 'ether')} WETH")
        mint_weth_to(LIQ, liq_topup)
    else:
        print("Liquidator already at or above target, skipping")

    if bor1_topup > 0:
        print(f"Top-up borrower 1 by {w3.from_wei(bor1_topup, 'ether')} WETH")
        mint_weth_to(BORROWER1, bor1_topup)
    else:
        print("Borrower 1 already at or above target, skipping")

    # Final balances
    liq_weth = weth.functions.balanceOf(LIQ).call()
    bor1_weth = weth.functions.balanceOf(BORROWER1).call()

    print("\nFinal balances:")
    print("Liquidator WETH (wei):", liq_weth)
    print("Liquidator WETH (ETH):", w3.from_wei(liq_weth, "ether"))
    print("Borrower 1 WETH (wei):", bor1_weth)
    print("Borrower 1 WETH (ETH):", w3.from_wei(bor1_weth, "ether"))


if __name__ == "__main__":
    main()
