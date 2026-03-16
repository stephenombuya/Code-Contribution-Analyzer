"""
Repository listing and per-repo analytics routes.
"""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.web.app import db, PlatformAccount, Analysis
from src.api_clients.github_client import GitHubClient
from src.api_clients.gitlab_client import GitLabClient
from src.api_clients.bitbucket_client import BitbucketClient

logger = logging.getLogger(__name__)
repos_bp = Blueprint("repos", __name__)


def _get_client(platform: str, access_token: str):
    return {
        "github": GitHubClient,
        "gitlab": GitLabClient,
        "bitbucket": BitbucketClient,
    }[platform](access_token)


@repos_bp.get("/<platform>")
@jwt_required()
def list_repos(platform: str):
    """List repositories for a connected platform account."""
    user_id = int(get_jwt_identity())
    pa = PlatformAccount.query.filter_by(user_id=user_id, platform=platform).first()
    if not pa:
        return jsonify({"error": f"No {platform} account connected."}), 403

    include_private = request.args.get("include_private", "true").lower() == "true"
    try:
        client = _get_client(platform, pa.access_token)
        repos = client.list_repositories(
            username=pa.username, include_private=include_private
        )
        # Normalize to a common shape
        normalized = [_normalize_repo(r, platform) for r in repos]
        return jsonify({"repos": normalized, "total": len(normalized)})
    except Exception as exc:
        logger.error("Repo list failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


@repos_bp.get("/<platform>/<owner>/<path:repo_name>")
@jwt_required()
def get_repo(platform: str, owner: str, repo_name: str):
    """Fetch metadata + language breakdown for a single repo."""
    user_id = int(get_jwt_identity())
    pa = PlatformAccount.query.filter_by(user_id=user_id, platform=platform).first()
    if not pa:
        return jsonify({"error": f"No {platform} account connected."}), 403

    try:
        client = _get_client(platform, pa.access_token)
        repo = client.get_repository(owner, repo_name)
        if platform == "github":
            langs = client.get_repository_languages(owner, repo_name)
            repo["_languages"] = langs
        return jsonify(_normalize_repo(repo, platform))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def _normalize_repo(repo: dict, platform: str) -> dict:
    """Flatten platform-specific repo schema to a common shape."""
    if platform == "github":
        owner_login = (repo.get("owner") or {}).get("login", "")
        return {
            "id": repo.get("id"),
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "owner": owner_login,
            "description": repo.get("description") or "",
            "language": repo.get("language") or "Unknown",
            "languages": repo.get("_languages", {}),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "is_private": repo.get("private", False),
            "url": repo.get("html_url", ""),
            "clone_url": repo.get("clone_url", ""),
            "created_at": repo.get("created_at", ""),
            "updated_at": repo.get("updated_at", ""),
            "platform": "github",
        }
    elif platform == "gitlab":
        ns = repo.get("namespace") or {}
        return {
            "id": repo.get("id"),
            "name": repo.get("name"),
            "full_name": repo.get("path_with_namespace"),
            "owner": ns.get("path", ""),
            "description": repo.get("description") or "",
            "language": repo.get("default_branch", ""),
            "languages": {},
            "stars": repo.get("star_count", 0),
            "forks": repo.get("forks_count", 0),
            "is_private": repo.get("visibility") == "private",
            "url": repo.get("web_url", ""),
            "clone_url": repo.get("http_url_to_repo", ""),
            "created_at": repo.get("created_at", ""),
            "updated_at": repo.get("last_activity_at", ""),
            "platform": "gitlab",
        }
    elif platform == "bitbucket":
        ws = repo.get("workspace") or {}
        links = repo.get("links") or {}
        html = (links.get("html") or {}).get("href", "")
        return {
            "id": repo.get("uuid", ""),
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "owner": ws.get("slug", ""),
            "description": repo.get("description") or "",
            "language": repo.get("language") or "Unknown",
            "languages": {},
            "stars": 0,
            "forks": 0,
            "is_private": repo.get("is_private", False),
            "url": html,
            "clone_url": "",
            "created_at": repo.get("created_on", ""),
            "updated_at": repo.get("updated_on", ""),
            "platform": "bitbucket",
        }
    return repo
