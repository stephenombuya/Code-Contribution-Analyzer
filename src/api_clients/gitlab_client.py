"""
GitLab API v4 client.
"""
from __future__ import annotations

import logging
from typing import Any, Iterator

from src.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class GitLabClient(BaseAPIClient):
    platform = "gitlab"

    def __init__(self, access_token: str, base_url: str = "https://gitlab.com") -> None:
        self.base_url = f"{base_url.rstrip('/')}/api/v4"
        super().__init__(access_token)

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

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

    # ── Repositories (Projects) ───────────────────────────────────────────────

    def list_repositories(
        self,
        username: str | None = None,
        include_private: bool = True,
    ) -> list[dict[str, Any]]:
        if username:
            user_info = self._get(f"/users?username={username}")
            if not user_info:
                return []
            user_id = user_info[0]["id"]
            endpoint = f"/users/{user_id}/projects"
        else:
            endpoint = "/projects"
        params: dict[str, Any] = {
            "membership": True,
            "order_by": "last_activity_at",
            "sort": "desc",
        }
        if not include_private:
            params["visibility"] = "public"
        projects = self._paginate_all(endpoint, params=params)
        logger.info("Fetched %d GitLab projects.", len(projects))
        return projects

    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        project_path = f"{owner}/{repo}".replace("/", "%2F")
        return self._get(f"/projects/{project_path}")

    def get_repository_languages(
        self, project_id: int | str
    ) -> dict[str, float]:
        """Returns {language: percentage} breakdown."""
        return self._get(f"/projects/{project_id}/languages")

    # ── Commits ───────────────────────────────────────────────────────────────

    def list_commits(
        self,
        owner: str,
        repo: str,
        author: str | None = None,
        since: str | None = None,
        until: str | None = None,
    ) -> list[dict[str, Any]]:
        project_path = f"{owner}/{repo}".replace("/", "%2F")
        params: dict[str, Any] = {"with_stats": True}
        if author:
            params["author"] = author
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        try:
            return self._paginate_all(
                f"/projects/{project_path}/repository/commits", params=params
            )
        except Exception as exc:
            logger.warning("Could not list GitLab commits for %s/%s: %s", owner, repo, exc)
            return []

    def get_commit(self, owner: str, repo: str, sha: str) -> dict[str, Any]:
        project_path = f"{owner}/{repo}".replace("/", "%2F")
        return self._get(
            f"/projects/{project_path}/repository/commits/{sha}",
            params={"stats": True},
        )

    def get_commit_stats(self, owner: str, repo: str, sha: str) -> dict[str, Any]:
        commit = self.get_commit(owner, repo, sha)
        stats = commit.get("stats", {})
        return {
            "sha": sha,
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0),
        }

    # ── Contributors ──────────────────────────────────────────────────────────

    def get_repository_contributors(
        self, project_id: int | str
    ) -> list[dict[str, Any]]:
        return self._paginate_all(f"/projects/{project_id}/repository/contributors")
