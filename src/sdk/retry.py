"""
sdk/retry.py

Retry helpers for making Web3 / JSON-RPC calls more robust.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, Iterable, Type


def retry_rpc(
    retries: int = 3,
    delay: float = 0.2,
    exceptions: Iterable[Type[BaseException]] = (Exception,),
) -> Callable:
    """
    Decorator to retry a function call on failure.

    Args:
        retries:   number of attempts in total
        delay:     seconds to sleep between attempts
        exceptions: tuple/list of exception types to catch

    Usage:
        @retry_rpc(retries=3, delay=0.1)
        def read_balance(...):
            return contract.functions.balanceOf(user).call()
    """

    exceptions = tuple(exceptions)

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_err: BaseException | None = None
            for attempt in range(retries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:  # type: ignore[misc]
                    last_err = e
                    if attempt < retries - 1:
                        time.sleep(delay)
                    else:
                        # Exhausted retries
                        raise
            # Should never reach here
            if last_err:
                raise last_err
        return wrapper
    return decorator


def safe_call(
    fn: Callable[..., Any],
    *args: Any,
    retries: int = 3,
    delay: float = 0.2,
    exceptions: Iterable[Type[BaseException]] = (Exception,),
    **kwargs: Any,
) -> Any:
    """
    Retry a function call manually, without using the decorator syntax.

    Usage:
        balance = safe_call(
            contract.functions.balanceOf(user).call,
            retries=3,
            delay=0.1,
        )
    """
    exceptions = tuple(exceptions)
    last_err: BaseException | None = None

    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except exceptions as e:  # type: ignore[misc]
            last_err = e
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise
    if last_err:
        raise last_err
