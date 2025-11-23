"""
sdk/addresses.py

Helpers for working safely with Ethereum addresses.
"""

from web3 import Web3


def to_checksum(addr: str) -> str:
    """
    Convert a hex address string to its EIP-55 checksummed form.

    Raises:
        TypeError  - if addr is not a string
        ValueError - if addr is not a valid 20-byte hex address
    """
    if not isinstance(addr, str):
        raise TypeError("Address must be a string")

    if not addr.startswith("0x"):
        raise ValueError(f"Invalid address (missing 0x prefix): {addr}")

    if len(addr) != 42:  # 2 + 40 hex chars
        raise ValueError(f"Invalid address length: {addr} (len={len(addr)})")

    # Will raise ValueError if the hex is malformed (non-hex chars etc.)
    return Web3.to_checksum_address(addr)


def validate_address(addr: str) -> None:
    """
    Validate that an address string is a valid EVM address.

    This wraps to_checksum() and discards the result; it is useful
    for 'assert-only' checks.
    """
    _ = to_checksum(addr)
