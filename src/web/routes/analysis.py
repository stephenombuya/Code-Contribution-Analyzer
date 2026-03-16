"""
Analysis API routes — trigger, poll, and retrieve contribution analyses.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.web.app import db, Analysis, PlatformAccount
from src.api_clients.github_client import GitHubClient
from src.api_clients.gitlab_client import GitLabClient
from src.api_clients.bitbucket_client import BitbucketClient
from src.analysis.contribution_analyzer import ContributionAnalyzer

logger = logging.getLogger(__name__)
analysis_bp = Blueprint("analysis", __name__)


def _get_client(platform: str, access_token: str):
    clients = {
        "github": GitHubClient,
        "gitlab": GitLabClient,
        "bitbucket": BitbucketClient,
    }
    cls = clients.get(platform)
    if not cls:
        raise ValueError(f"Unsupported platform: {platform}")
    return cls(access_token)


@analysis_bp.post("/run")
@jwt_required()
def run_analysis():
    """
    Trigger a new analysis synchronously (for small repos).
    Body: { platform, since?, until?, max_repos?, include_private? }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    platform = data.get("platform")

    if not platform:
        return jsonify({"error": "platform is required."}), 400

    pa = PlatformAccount.query.filter_by(user_id=user_id, platform=platform).first()
    if not pa:
        return jsonify({
            "error": f"No {platform} account connected. Please connect it first."
        }), 403

    analysis = Analysis(
        user_id=user_id,
        platform=platform,
        username=pa.username,
        status="running",
        since=data.get("since"),
        until=data.get("until"),
        started_at=datetime.now(timezone.utc),
    )
    db.session.add(analysis)
    db.session.commit()

    try:
        client = _get_client(platform, pa.access_token)
        analyzer = ContributionAnalyzer(client, pa.username)
        summary = analyzer.analyze(
            since=data.get("since"),
            until=data.get("until"),
            max_repos=int(data.get("max_repos", 50)),
            include_private=data.get("include_private", True),
        )

        analysis.result = summary.to_dict()
        analysis.status = "completed"
        analysis.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({
            "analysis_id": analysis.id,
            "status": "completed",
            "result": summary.to_dict(),
        })

    except Exception as exc:
        logger.error("Analysis failed for user %d on %s: %s", user_id, platform, exc)
        analysis.status = "failed"
        analysis.error = str(exc)
        analysis.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"error": str(exc), "analysis_id": analysis.id}), 500


@analysis_bp.get("/")
@jwt_required()
def list_analyses():
    """List all analyses for the current user."""
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    platform = request.args.get("platform")

    q = Analysis.query.filter_by(user_id=user_id)
    if platform:
        q = q.filter_by(platform=platform)
    q = q.order_by(Analysis.created_at.desc())
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "analyses": [a.to_dict() for a in paginated.items],
        "total": paginated.total,
        "page": page,
        "pages": paginated.pages,
    })


@analysis_bp.get("/<int:analysis_id>")
@jwt_required()
def get_analysis(analysis_id: int):
    """Get a specific analysis, optionally including full result."""
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found."}), 404

    include_result = request.args.get("include_result", "true").lower() == "true"
    return jsonify(analysis.to_dict(include_result=include_result))


@analysis_bp.delete("/<int:analysis_id>")
@jwt_required()
def delete_analysis(analysis_id: int):
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found."}), 404
    db.session.delete(analysis)
    db.session.commit()
    return jsonify({"message": "Analysis deleted."})


@analysis_bp.get("/latest/<platform>")
@jwt_required()
def get_latest(platform: str):
    """Get the most recent completed analysis for a platform."""
    user_id = int(get_jwt_identity())
    analysis = (
        Analysis.query.filter_by(user_id=user_id, platform=platform, status="completed")
        .order_by(Analysis.completed_at.desc())
        .first()
    )
    if not analysis:
        return jsonify({"error": "No completed analysis found."}), 404
    return jsonify(analysis.to_dict(include_result=True))


@analysis_bp.get("/summary/all")
@jwt_required()
def get_combined_summary():
    """
    Return an aggregated summary across all platforms the user has analyzed.
    """
    user_id = int(get_jwt_identity())

    # Get latest completed analysis per platform
    platforms = ["github", "gitlab", "bitbucket"]
    summaries: list[dict] = []

    for platform in platforms:
        a = (
            Analysis.query.filter_by(
                user_id=user_id, platform=platform, status="completed"
            )
            .order_by(Analysis.completed_at.desc())
            .first()
        )
        if a and a.result:
            summaries.append(a.result)

    if not summaries:
        return jsonify({"error": "No completed analyses found."}), 404

    # Merge
    total_repos = sum(s.get("total_repos", 0) for s in summaries)
    total_commits = sum(s.get("total_commits", 0) for s in summaries)
    total_additions = sum(s.get("total_additions", 0) for s in summaries)
    total_deletions = sum(s.get("total_deletions", 0) for s in summaries)

    merged_langs: dict[str, int] = {}
    for s in summaries:
        for lang, val in (s.get("languages") or {}).items():
            merged_langs[lang] = merged_langs.get(lang, 0) + (val or 0)

    top_langs = sorted(merged_langs.items(), key=lambda x: x[1], reverse=True)[:15]

    return jsonify({
        "total_repos": total_repos,
        "total_commits": total_commits,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "net_lines": total_additions - total_deletions,
        "top_languages": dict(top_langs),
        "platforms_analyzed": [s["platform"] for s in summaries],
    })
