"""
sdk/clients.py

Central place to create and cache Web3 clients.

Responsibilities
- Load RPC URL from .env (or accept an override).
- Expose a single HTTP Web3 client via get_w3().
- Optionally expose a WebSocket client via get_w3_ws() for later use.
- Attach basic configuration (timeouts, place to add middleware).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from web3 import Web3, HTTPProvider, WebSocketProvider

# ---------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------

# Load .env from project root (two levels up: src/sdk -> src -> project)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

_DEFAULT_RPC_URL = os.getenv("RPC_URL")


# ---------------------------------------------------------------------
# Internal cached clients
# ---------------------------------------------------------------------

_http_client: Optional[Web3] = None
_ws_client: Optional[Web3] = None


# ---------------------------------------------------------------------
# HTTP client factory
# ---------------------------------------------------------------------

def _make_http_client(rpc_url: str) -> Web3:
    """
    Create a fresh HTTP Web3 client.

    This is kept internal; external code should use get_w3() so that
    all callers share a single, cached instance.
    """
    if not rpc_url:
        raise RuntimeError(
            "RPC_URL is not set. "
            "Set RPC_URL in your .env file or pass rpc_url= explicitly."
        )

    # You can tweak timeout here if you like (default ~10s).
    provider = HTTPProvider(rpc_url, request_kwargs={"timeout": 30})

    w3 = Web3(provider)

    # Place to add middleware later, for example:
    # from web3.middleware import geth_poa_middleware
    # w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    if not w3.is_connected():
        raise RuntimeError(f"Web3 HTTP client could not connect to {rpc_url}")

    return w3


def get_w3(rpc_url: Optional[str] = None) -> Web3:
    """
    Return a singleton HTTP Web3 client.

    - Uses RPC_URL from .env by default.
    - Caches the client so the whole project shares one instance.
    - Accepts an override rpc_url for tests if needed.
    """
    global _http_client

    if _http_client is not None and rpc_url is None:
        return _http_client

    url = rpc_url or _DEFAULT_RPC_URL
    _http_client = _make_http_client(url)
    return _http_client


# ---------------------------------------------------------------------
# WebSocket client factory (optional, for later event listeners)
# ---------------------------------------------------------------------

def _make_ws_client(rpc_ws_url: str) -> Web3:
    """
    Create a fresh WebSocket Web3 client.

    Only needed if you later use WebSocket-based event listeners.
    """
    if not rpc_ws_url:
        raise RuntimeError(
            "WebSocket RPC URL is not set. "
            "Pass rpc_ws_url= explicitly when calling get_w3_ws()."
        )

    provider = WebsocketProvider(rpc_ws_url)
    w3 = Web3(provider)

    if not w3.is_connected():
        raise RuntimeError(f"Web3 WS client could not connect to {rpc_ws_url}")

    return w3


def get_w3_ws(rpc_ws_url: str) -> Web3:
    """
    Return a singleton WebSocket Web3 client.

    You must explicitly pass the WS URL (e.g. from config) because
    not all setups use WebSocket endpoints.
    """
    global _ws_client

    if _ws_client is not None:
        return _ws_client

    _ws_client = _make_ws_client(rpc_ws_url)
    return _ws_client
