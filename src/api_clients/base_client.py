"""
Base API client — shared session management, auth headers, pagination helpers.
All platform-specific clients inherit from this.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Generator, Iterator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils.rate_limiter import get_limiter, handle_response

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30  # seconds


def _build_session(retries: int = 3) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class BaseAPIClient(ABC):
    """Abstract base for all platform API clients."""

    platform: str = "base"
    base_url: str = ""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self._session = _build_session()
        self._limiter = get_limiter(self.platform)
        logger.debug("Initialised %s API client.", self.platform)

    # ── Auth ──────────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def auth_headers(self) -> dict[str, str]:
        """Return HTTP headers required for authentication."""

    # ── Low-level request ─────────────────────────────────────────────────────

    def _get(
        self,
        endpoint: str,
        params: dict | None = None,
        full_url: str | None = None,
    ) -> Any:
        """Make an authenticated GET request and return parsed JSON."""
        url = full_url or urljoin(self.base_url + "/", endpoint.lstrip("/"))
        self._limiter.wait_if_needed()
        response = self._session.get(
            url,
            headers={**self.auth_headers, "Accept": "application/json"},
            params=params or {},
            timeout=DEFAULT_TIMEOUT,
        )
        handle_response(response, self.platform)
        self._limiter.update_from_headers(dict(response.headers))
        return response.json()

    def _post(self, endpoint: str, data: dict | None = None) -> Any:
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        self._limiter.wait_if_needed()
        response = self._session.post(
            url,
            headers=self.auth_headers,
            json=data or {},
            timeout=DEFAULT_TIMEOUT,
        )
        handle_response(response, self.platform)
        return response.json()

    # ── Pagination ────────────────────────────────────────────────────────────

    def _paginate(
        self,
        endpoint: str,
        params: dict | None = None,
        per_page: int = 100,
    ) -> Iterator[list[Any]]:
        """Yield pages of results, handling cursor/page-based pagination."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _paginate()"
        )

    def _paginate_all(
        self,
        endpoint: str,
        params: dict | None = None,
        per_page: int = 100,
    ) -> list[Any]:
        """Collect all pages into a single list."""
        results: list[Any] = []
        for page in self._paginate(endpoint, params=params, per_page=per_page):
            results.extend(page)
        return results

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def get_authenticated_user(self) -> dict[str, Any]:
        """Return the authenticated user's profile."""

    @abstractmethod
    def list_repositories(
        self, username: str | None = None, include_private: bool = True
    ) -> list[dict[str, Any]]:
        """List repositories accessible to the authenticated user."""

    @abstractmethod
    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch metadata for a single repository."""

    @abstractmethod
    def list_commits(
        self,
        owner: str,
        repo: str,
        author: str | None = None,
        since: str | None = None,
        until: str | None = None,
    ) -> list[dict[str, Any]]:
        """List commits in a repository, optionally filtered by author/date."""

    @abstractmethod
    def get_commit(self, owner: str, repo: str, sha: str) -> dict[str, Any]:
        """Fetch a single commit with diff stats."""

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "BaseAPIClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
