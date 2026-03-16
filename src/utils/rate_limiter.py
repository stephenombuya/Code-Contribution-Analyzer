"""
API rate-limit handling with exponential back-off and per-platform quotas.
"""
from __future__ import annotations

import time
import functools
import logging
from typing import Callable, TypeVar, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import requests

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# ── Per-platform rate state ────────────────────────────────────────────────────

class RateLimitExceeded(Exception):
    """Raised when a platform rate limit is hit."""

    def __init__(self, platform: str, retry_after: int = 60):
        self.platform = platform
        self.retry_after = retry_after
        super().__init__(
            f"{platform} rate limit exceeded. Retry after {retry_after}s."
        )


class PlatformRateLimiter:
    """
    Token-bucket rate limiter per platform.
    Tracks remaining quota from response headers.
    """

    def __init__(self, platform: str, default_delay: float = 0.5):
        self.platform = platform
        self.default_delay = default_delay
        self._remaining: int | None = None
        self._reset_at: float = 0.0
        self._last_call: float = 0.0

    def update_from_headers(self, headers: dict) -> None:
        """Parse rate-limit headers from API responses."""
        # GitHub / GitLab style
        remaining = headers.get("X-RateLimit-Remaining") or headers.get(
            "RateLimit-Remaining"
        )
        reset = headers.get("X-RateLimit-Reset") or headers.get("RateLimit-Reset")

        if remaining is not None:
            self._remaining = int(remaining)
        if reset is not None:
            self._reset_at = float(reset)

    def wait_if_needed(self) -> None:
        """Sleep if we're near the rate limit or too close to the last call."""
        now = time.time()

        # Minimum delay between calls
        elapsed = now - self._last_call
        if elapsed < self.default_delay:
            time.sleep(self.default_delay - elapsed)

        # If quota almost exhausted, sleep until reset
        if self._remaining is not None and self._remaining <= 5:
            wait = max(0, self._reset_at - time.time())
            if wait > 0:
                logger.warning(
                    "%s rate limit almost exhausted (%d remaining). Sleeping %.1fs.",
                    self.platform,
                    self._remaining,
                    wait,
                )
                time.sleep(wait + 1)

        self._last_call = time.time()


# Singleton instances per platform
_limiters: dict[str, PlatformRateLimiter] = {}


def get_limiter(platform: str) -> PlatformRateLimiter:
    if platform not in _limiters:
        delays = {"github": 0.3, "gitlab": 0.5, "bitbucket": 0.5}
        _limiters[platform] = PlatformRateLimiter(
            platform, default_delay=delays.get(platform, 0.5)
        )
    return _limiters[platform]


# ── Retry decorator ───────────────────────────────────────────────────────────

def with_retry(
    platform: str = "api",
    max_attempts: int = 5,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
) -> Callable[[F], F]:
    """Decorator: retry with exponential back-off on transient errors."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(
                (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter = get_limiter(platform)
            limiter.wait_if_needed()
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def handle_response(response: requests.Response, platform: str) -> requests.Response:
    """
    Update rate-limit state from response headers and raise on HTTP errors.
    Returns the response unchanged so callers can chain.
    """
    limiter = get_limiter(platform)
    limiter.update_from_headers(dict(response.headers))

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitExceeded(platform, retry_after)

    response.raise_for_status()
    return response
