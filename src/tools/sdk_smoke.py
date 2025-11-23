"""
Quick SDK smoke test.

- Uses get_w3() from sdk.clients
- Loads ERC20 ABI via sdk.abi_loader.get_contract
- Uses checksummed address helper
- Optionally wraps a call with safe_call
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
import os

# ---------------------------------------------------------------------
# Ensure project-root/src is on sys.path
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sdk.clients import get_w3
from sdk.abi_loader import get_contract
from sdk.addresses import to_checksum
from sdk.retry import safe_call


def main() -> None:
    # Load .env from project root
    load_dotenv(PROJECT_ROOT / ".env")

    # These should already exist in your .env
    rpc = os.getenv("RPC_URL")
    weth_addr = os.getenv("WETH_ADDRESS") or "0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2"
    test_account = os.getenv("LIQUIDATOR_ADDRESS")  # or any funded address on your fork

    if not rpc:
        raise RuntimeError("RPC_URL not set in .env")
    if not test_account:
        raise RuntimeError("LIQUIDATOR_ADDRESS not set in .env")

    print("Using RPC:", rpc)
    print("WETH address:", weth_addr)
    print("Test account:", test_account)

    w3 = get_w3()
    print("Connected:", w3.is_connected())

    weth = get_contract(w3, weth_addr, "erc20")

    # Simple sanity: check decimals
    decimals = safe_call(weth.functions.decimals().call)
    print("WETH decimals:", decimals)

    # Check balance of the test account
    checksum_user = to_checksum(test_account)
    raw_balance = safe_call(weth.functions.balanceOf(checksum_user).call)

    human_balance = raw_balance / (10 ** decimals)
    print(f"WETH balance of {checksum_user}:")
    print("  raw (wei):", raw_balance)
    print("  human   :", human_balance)


if __name__ == "__main__":
    main()
