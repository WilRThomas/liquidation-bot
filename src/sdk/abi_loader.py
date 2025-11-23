"""
sdk/abi_loader.py

Utilities for loading ABI JSON files and constructing Web3 contract objects.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from web3 import Web3
from web3.contract import Contract

from .addresses import to_checksum


# ---------------------------------------------------------------------
# Locate ABI directory: src/abi/
# ---------------------------------------------------------------------

ABI_DIR = Path(__file__).resolve().parents[1] / "abi"

# Cache ABI results in memory (faster repeated loads)
_ABI_CACHE: Dict[str, List[Dict[str, Any]]] = {}


# ---------------------------------------------------------------------
# Load ABI JSON by name
# ---------------------------------------------------------------------

def load_abi(name: str) -> List[Dict[str, Any]]:
    """
    Load an ABI JSON file from src/abi/{name}.json.

    Example:
        erc20_abi = load_abi("erc20")
    """
    if name in _ABI_CACHE:
        return _ABI_CACHE[name]

    path = ABI_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"ABI file not found: {path}")

    with path.open() as f:
        abi = json.load(f)

    if not isinstance(abi, list):
        raise ValueError(f"ABI file {path} must contain a JSON list.")

    _ABI_CACHE[name] = abi
    return abi


# ---------------------------------------------------------------------
# Construct Web3 contract objects
# ---------------------------------------------------------------------

def get_contract(w3: Web3, address: str, abi_name: str) -> Contract:
    """
    Return a Web3 contract instance using an ABI name.

    Example:
        weth = get_contract(w3, WETH_ADDRESS, "erc20")
        data = weth.functions.balanceOf(user).call()
    """
    checksum = to_checksum(address)
    abi = load_abi(abi_name)
    return w3.eth.contract(address=checksum, abi=abi)
