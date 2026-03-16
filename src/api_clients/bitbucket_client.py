"""
Bitbucket Cloud REST API 2.0 client.
"""
from __future__ import annotations

import logging
from typing import Any, Iterator

from src.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class BitbucketClient(BaseAPIClient):
    platform = "bitbucket"
    base_url = "https://api.bitbucket.org/2.0"

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    # ── Pagination (cursor-based) ─────────────────────────────────────────────

    def _paginate(
        self,
        endpoint: str,
        params: dict | None = None,
        per_page: int = 100,
    ) -> Iterator[list[Any]]:
        p = {**(params or {}), "pagelen": per_page}
        next_url: str | None = None
        while True:
            if next_url:
                result = self._get(endpoint, full_url=next_url)
            else:
                result = self._get(endpoint, params=p)
            values = result.get("values", [])
            if not values:
                break
            yield values
            next_url = result.get("next")
            if not next_url:
                break

    # ── User ──────────────────────────────────────────────────────────────────

    def get_authenticated_user(self) -> dict[str, Any]:
        return self._get("/user")

    # ── Repositories ──────────────────────────────────────────────────────────

    def list_repositories(
        self,
        username: str | None = None,
        include_private: bool = True,
    ) -> list[dict[str, Any]]:
        workspace = username or self._get_workspace()
        endpoint = f"/repositories/{workspace}"
        params: dict[str, Any] = {"sort": "-updated_on"}
        if not include_private:
            params["q"] = 'is_private=false'
        repos = self._paginate_all(endpoint, params=params)
        logger.info("Fetched %d Bitbucket repositories.", len(repos))
        return repos

    def _get_workspace(self) -> str:
        user = self.get_authenticated_user()
        return user.get("username") or user.get("account_id", "")

    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        return self._get(f"/repositories/{owner}/{repo}")

    # ── Commits ───────────────────────────────────────────────────────────────

    def list_commits(
        self,
        owner: str,
        repo: str,
        author: str | None = None,
        since: str | None = None,
        until: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if author:
            params["q"] = f'author.user.username="{author}"'
        try:
            return self._paginate_all(
                f"/repositories/{owner}/{repo}/commits", params=params
            )
        except Exception as exc:
            logger.warning(
                "Could not list Bitbucket commits for %s/%s: %s", owner, repo, exc
            )
            return []

    def get_commit(self, owner: str, repo: str, sha: str) -> dict[str, Any]:
        return self._get(f"/repositories/{owner}/{repo}/commit/{sha}")

    def get_commit_stats(self, owner: str, repo: str, sha: str) -> dict[str, Any]:
        """Bitbucket doesn't expose per-commit stats directly via REST; parse diff."""
        diff = self._get(f"/repositories/{owner}/{repo}/diff/{sha}")
        # diff is raw text — count +/- lines
        additions = deletions = 0
        if isinstance(diff, str):
            for line in diff.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    additions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    deletions += 1
        return {
            "sha": sha,
            "additions": additions,
            "deletions": deletions,
            "total": additions + deletions,
        }

    # ── Languages ─────────────────────────────────────────────────────────────

    def get_repository_languages(
        self, owner: str, repo: str
    ) -> dict[str, Any]:
        """Bitbucket exposes a limited set; returns whatever it has."""
        try:
            info = self.get_repository(owner, repo)
            lang = info.get("language")
            return {lang: 100} if lang else {}
        except Exception:
            return {}
