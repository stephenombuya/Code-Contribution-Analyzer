"""
GitHub API v3 client.
Supports both OAuth tokens and Personal Access Tokens.
"""
from __future__ import annotations

import logging
from typing import Any, Iterator

from src.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class GitHubClient(BaseAPIClient):
    platform = "github"
    base_url = "https://api.github.com"

    @property
    def auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ── Pagination ────────────────────────────────────────────────────────────

    def _paginate(
        self,
        endpoint: str,
        params: dict | None = None,
        per_page: int = 100,
    ) -> Iterator[list[Any]]:
        page = 1
        p = {**(params or {}), "per_page": per_page, "page": page}
        while True:
            p["page"] = page
            results = self._get(endpoint, params=p)
            if not results:
                break
            yield results
            if len(results) < per_page:
                break
            page += 1

    # ── User ──────────────────────────────────────────────────────────────────

    def get_authenticated_user(self) -> dict[str, Any]:
        return self._get("/user")

    def get_user(self, username: str) -> dict[str, Any]:
        return self._get(f"/users/{username}")

    # ── Repositories ──────────────────────────────────────────────────────────

    def list_repositories(
        self,
        username: str | None = None,
        include_private: bool = True,
    ) -> list[dict[str, Any]]:
        if username:
            endpoint = f"/users/{username}/repos"
            params = {"type": "all", "sort": "updated"}
        else:
            endpoint = "/user/repos"
            visibility = "all" if include_private else "public"
            params = {"visibility": visibility, "affiliation": "owner,collaborator", "sort": "updated"}

        repos = self._paginate_all(endpoint, params=params)
        logger.info("Fetched %d GitHub repositories.", len(repos))
        return repos

    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        return self._get(f"/repos/{owner}/{repo}")

    def get_repository_languages(self, owner: str, repo: str) -> dict[str, int]:
        """Returns {language: bytes} breakdown."""
        return self._get(f"/repos/{owner}/{repo}/languages")

    def get_repository_contributors(
        self, owner: str, repo: str
    ) -> list[dict[str, Any]]:
        return self._paginate_all(f"/repos/{owner}/{repo}/contributors")

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
            params["author"] = author
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        try:
            return self._paginate_all(f"/repos/{owner}/{repo}/commits", params=params)
        except Exception as exc:
            logger.warning("Could not list commits for %s/%s: %s", owner, repo, exc)
            return []

    def get_commit(self, owner: str, repo: str, sha: str) -> dict[str, Any]:
        return self._get(f"/repos/{owner}/{repo}/commits/{sha}")

    def get_commit_stats(
        self, owner: str, repo: str, sha: str
    ) -> dict[str, Any]:
        """Return additions/deletions/total for a specific commit."""
        commit = self.get_commit(owner, repo, sha)
        stats = commit.get("stats", {})
        files = commit.get("files", [])
        return {
            "sha": sha,
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0),
            "files": [
                {
                    "filename": f.get("filename"),
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "status": f.get("status"),
                }
                for f in files
            ],
        }

    # ── Contents ──────────────────────────────────────────────────────────────

    def get_tree(
        self, owner: str, repo: str, tree_sha: str = "HEAD", recursive: bool = True
    ) -> list[dict[str, Any]]:
        params = {"recursive": "1"} if recursive else {}
        result = self._get(
            f"/repos/{owner}/{repo}/git/trees/{tree_sha}", params=params
        )
        return result.get("tree", [])

    def get_contents(
        self, owner: str, repo: str, path: str = ""
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return self._get(f"/repos/{owner}/{repo}/contents/{path}")

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_contributor_stats(
        self, owner: str, repo: str
    ) -> list[dict[str, Any]]:
        """Weekly commit activity per contributor."""
        try:
            return self._get(f"/repos/{owner}/{repo}/stats/contributors") or []
        except Exception:
            return []

    def get_code_frequency(self, owner: str, repo: str) -> list[list[int]]:
        """Weekly additions/deletions time series [[timestamp, add, del], ...]."""
        try:
            return self._get(f"/repos/{owner}/{repo}/stats/code_frequency") or []
        except Exception:
            return []

    def get_commit_activity(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Last 52 weeks of commit counts."""
        try:
            return self._get(f"/repos/{owner}/{repo}/stats/commit_activity") or []
        except Exception:
            return []
