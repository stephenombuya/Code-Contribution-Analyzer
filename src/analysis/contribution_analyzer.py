"""
Core contribution analysis engine.
Aggregates commit stats, language breakdowns, and time-series data
from a given platform client.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from src.api_clients.base_client import BaseAPIClient
from src.api_clients.github_client import GitHubClient

logger = logging.getLogger(__name__)


@dataclass
class CommitStat:
    sha: str
    message: str
    date: str
    additions: int
    deletions: int
    total: int
    repo: str
    platform: str


@dataclass
class RepoAnalysis:
    platform: str
    owner: str
    name: str
    full_name: str
    description: str
    language: str
    languages: dict[str, Any]
    stars: int
    forks: int
    is_private: bool
    created_at: str
    updated_at: str
    clone_url: str
    total_commits: int = 0
    user_commits: int = 0
    user_additions: int = 0
    user_deletions: int = 0
    contributors: list[dict] = field(default_factory=list)
    weekly_stats: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class ContributionSummary:
    platform: str
    username: str
    total_repos: int
    total_commits: int
    total_additions: int
    total_deletions: int
    net_lines: int
    languages: dict[str, int]   # language → net LOC
    repos: list[dict]
    monthly_activity: list[dict]  # [{month, commits, additions, deletions}]
    top_repos: list[dict]

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class ContributionAnalyzer:
    """
    High-level analyzer: takes an API client and a username,
    produces full contribution analytics.
    """

    def __init__(self, client: BaseAPIClient, username: str) -> None:
        self.client = client
        self.username = username
        self.platform = client.platform

    # ── Public interface ──────────────────────────────────────────────────────

    def analyze(
        self,
        since: str | None = None,
        until: str | None = None,
        max_repos: int = 50,
        include_private: bool = True,
    ) -> ContributionSummary:
        """Run full analysis and return a ContributionSummary."""
        logger.info(
            "Starting %s analysis for '%s' (since=%s until=%s).",
            self.platform, self.username, since, until,
        )

        repos = self.client.list_repositories(
            username=self.username, include_private=include_private
        )[:max_repos]

        analyzed_repos: list[dict] = []
        language_totals: dict[str, int] = defaultdict(int)
        total_commits = total_additions = total_deletions = 0
        monthly: dict[str, dict[str, int]] = defaultdict(
            lambda: {"commits": 0, "additions": 0, "deletions": 0}
        )

        for repo_data in repos:
            try:
                ra = self._analyze_repo(repo_data, since=since, until=until)
                analyzed_repos.append(ra.to_dict())
                total_commits += ra.user_commits
                total_additions += ra.user_additions
                total_deletions += ra.user_deletions
                for lang, info in ra.languages.items():
                    if isinstance(info, dict):
                        language_totals[lang] += info.get("lines", 0)
                    elif isinstance(info, (int, float)):
                        language_totals[lang] += int(info)
                for ws in ra.weekly_stats:
                    month = ws.get("month", "")
                    if month:
                        monthly[month]["commits"] += ws.get("commits", 0)
                        monthly[month]["additions"] += ws.get("additions", 0)
                        monthly[month]["deletions"] += ws.get("deletions", 0)
            except Exception as exc:
                logger.warning("Failed to analyze repo %s: %s", repo_data.get("name"), exc)

        monthly_list = [
            {"month": k, **v}
            for k, v in sorted(monthly.items())
        ]

        top_repos = sorted(
            analyzed_repos, key=lambda r: r.get("user_commits", 0), reverse=True
        )[:10]

        return ContributionSummary(
            platform=self.platform,
            username=self.username,
            total_repos=len(analyzed_repos),
            total_commits=total_commits,
            total_additions=total_additions,
            total_deletions=total_deletions,
            net_lines=total_additions - total_deletions,
            languages=dict(language_totals),
            repos=analyzed_repos,
            monthly_activity=monthly_list,
            top_repos=top_repos,
        )

    # ── Per-repo analysis ─────────────────────────────────────────────────────

    def _analyze_repo(
        self,
        repo_data: dict,
        since: str | None = None,
        until: str | None = None,
    ) -> RepoAnalysis:
        owner, name = self._extract_owner_name(repo_data)
        logger.debug("Analyzing repo %s/%s on %s.", owner, name, self.platform)

        # Languages
        languages = self._get_languages(repo_data, owner, name)

        # Commits by this user
        commits = self.client.list_commits(
            owner, name, author=self.username, since=since, until=until
        )

        user_additions = user_deletions = 0
        weekly: dict[str, dict[str, int]] = defaultdict(
            lambda: {"commits": 0, "additions": 0, "deletions": 0}
        )

        # Sample stats from first N commits (avoid hammering API on huge repos)
        sample_limit = min(len(commits), 200)
        for commit in commits[:sample_limit]:
            sha = commit.get("sha") or commit.get("id") or ""
            date_str = self._extract_date(commit)
            month = date_str[:7] if date_str else "unknown"  # YYYY-MM

            additions = deletions = 0
            # GitHub embeds stats in list_commits response
            if self.platform == "github":
                stats = commit.get("stats", {})
                additions = stats.get("additions", 0)
                deletions = stats.get("deletions", 0)
            # GitLab embeds stats when with_stats=True
            elif self.platform == "gitlab":
                stats = commit.get("stats", {})
                additions = stats.get("additions", 0)
                deletions = stats.get("deletions", 0)

            user_additions += additions
            user_deletions += deletions
            weekly[month]["commits"] += 1
            weekly[month]["additions"] += additions
            weekly[month]["deletions"] += deletions

        weekly_list = [{"month": k, **v} for k, v in sorted(weekly.items())]

        return RepoAnalysis(
            platform=self.platform,
            owner=owner,
            name=name,
            full_name=f"{owner}/{name}",
            description=repo_data.get("description") or "",
            language=repo_data.get("language") or "",
            languages=languages,
            stars=repo_data.get("stargazers_count")
            or repo_data.get("star_count")
            or 0,
            forks=repo_data.get("forks_count") or repo_data.get("forks") or 0,
            is_private=repo_data.get("private") or repo_data.get("visibility") == "private" or False,
            created_at=repo_data.get("created_at") or "",
            updated_at=repo_data.get("updated_at") or repo_data.get("last_activity_at") or "",
            clone_url=repo_data.get("clone_url")
            or repo_data.get("http_url_to_repo")
            or repo_data.get("links", {}).get("clone", [{}])[0].get("href", ""),
            total_commits=len(commits),
            user_commits=len(commits),
            user_additions=user_additions,
            user_deletions=user_deletions,
            weekly_stats=weekly_list,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_owner_name(self, repo_data: dict) -> tuple[str, str]:
        """Extract (owner, name) from platform-specific repo dict."""
        if self.platform == "github":
            full = repo_data.get("full_name", "/")
            parts = full.split("/", 1)
            return parts[0], parts[1] if len(parts) > 1 else ""
        elif self.platform == "gitlab":
            ns = repo_data.get("namespace", {})
            return ns.get("path", ""), repo_data.get("path", "")
        elif self.platform == "bitbucket":
            ws = repo_data.get("workspace", {})
            return ws.get("slug", ""), repo_data.get("slug", "")
        return "", repo_data.get("name", "")

    def _get_languages(
        self, repo_data: dict, owner: str, name: str
    ) -> dict[str, Any]:
        try:
            if isinstance(self.client, GitHubClient):
                bytes_map = self.client.get_repository_languages(owner, name)
                total = sum(bytes_map.values()) or 1
                return {
                    lang: {"bytes": b, "pct": round(b / total * 100, 1)}
                    for lang, b in bytes_map.items()
                }
        except Exception as exc:
            logger.debug("Language fetch failed for %s/%s: %s", owner, name, exc)
        return {}

    @staticmethod
    def _extract_date(commit: dict) -> str:
        """Extract ISO date string from commit across platforms."""
        # GitHub
        ci = commit.get("commit", {})
        if ci:
            author = ci.get("author", {})
            return author.get("date", "")[:10]
        # GitLab
        if "authored_date" in commit:
            return commit["authored_date"][:10]
        # Bitbucket
        if "date" in commit:
            return commit["date"][:10]
        return ""
