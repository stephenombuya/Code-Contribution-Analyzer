"""
OAuth2 authentication routes for GitHub, GitLab, and Bitbucket.
Flow: /authorize → platform OAuth → /callback → JWT issued to frontend.
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests
from flask import Blueprint, current_app, jsonify, redirect, request, session
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from src.web.app import db, User, PlatformAccount

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

# ── OAuth configuration per platform ─────────────────────────────────────────

PLATFORM_CONFIG = {
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_url": "https://api.github.com/user",
        "scopes": "read:user user:email repo",
        "client_id_key": "GITHUB_CLIENT_ID",
        "client_secret_key": "GITHUB_CLIENT_SECRET",
    },
    "gitlab": {
        "authorize_url": "https://gitlab.com/oauth/authorize",
        "token_url": "https://gitlab.com/oauth/token",
        "user_url": "https://gitlab.com/api/v4/user",
        "scopes": "read_user read_api read_repository",
        "client_id_key": "GITLAB_CLIENT_ID",
        "client_secret_key": "GITLAB_CLIENT_SECRET",
    },
    "bitbucket": {
        "authorize_url": "https://bitbucket.org/site/oauth2/authorize",
        "token_url": "https://bitbucket.org/site/oauth2/access_token",
        "user_url": "https://api.bitbucket.org/2.0/user",
        "scopes": "account repositories",
        "client_id_key": "BITBUCKET_CLIENT_ID",
        "client_secret_key": "BITBUCKET_CLIENT_SECRET",
    },
}


def _callback_url(platform: str) -> str:
    frontend = current_app.config["FRONTEND_URL"]
    return f"{frontend}/auth/callback/{platform}"


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.get("/authorize/<platform>")
def authorize(platform: str):
    """Step 1: Redirect user to platform OAuth page."""
    cfg = PLATFORM_CONFIG.get(platform)
    if not cfg:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400

    client_id = current_app.config.get(cfg["client_id_key"])
    if not client_id:
        return jsonify({"error": f"{platform} OAuth not configured on this server."}), 503

    state = secrets.token_urlsafe(32)
    session[f"oauth_state_{platform}"] = state

    params = {
        "client_id": client_id,
        "redirect_uri": _callback_url(platform),
        "scope": cfg["scopes"],
        "state": state,
        "response_type": "code",
    }

    url = cfg["authorize_url"] + "?" + urlencode(params)
    return jsonify({"url": url})


@auth_bp.post("/callback/<platform>")
def callback(platform: str):
    """
    Step 2: Exchange OAuth code for access token.
    Frontend posts { code, state } here after platform redirects back.
    """
    cfg = PLATFORM_CONFIG.get(platform)
    if not cfg:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400

    data = request.get_json(silent=True) or {}
    code = data.get("code")
    state = data.get("state")

    if not code:
        return jsonify({"error": "Missing OAuth code."}), 400

    # Exchange code for access token
    client_id = current_app.config.get(cfg["client_id_key"])
    client_secret = current_app.config.get(cfg["client_secret_key"])

    token_resp = requests.post(
        cfg["token_url"],
        headers={"Accept": "application/json"},
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": _callback_url(platform),
            "grant_type": "authorization_code",
        },
        timeout=15,
    )

    if not token_resp.ok:
        logger.error("Token exchange failed: %s", token_resp.text)
        return jsonify({"error": "Token exchange failed."}), 502

    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return jsonify({"error": "No access token in response.", "detail": token_data}), 502

    # Fetch platform user profile
    user_info = _fetch_platform_user(cfg["user_url"], access_token, platform)
    if not user_info:
        return jsonify({"error": "Could not fetch user profile."}), 502

    # Upsert User + PlatformAccount
    user = _upsert_user(platform, user_info, access_token, token_data)

    # Issue JWTs
    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": user.to_dict(),
    })


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({"access_token": access})


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    accounts = [pa.to_dict() for pa in user.platform_accounts]
    data = user.to_dict()
    data["accounts"] = accounts
    return jsonify(data)


@auth_bp.delete("/disconnect/<platform>")
@jwt_required()
def disconnect(platform: str):
    user_id = int(get_jwt_identity())
    pa = PlatformAccount.query.filter_by(user_id=user_id, platform=platform).first()
    if pa:
        db.session.delete(pa)
        db.session.commit()
    return jsonify({"message": f"Disconnected from {platform}."})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_platform_user(
    user_url: str, access_token: str, platform: str
) -> dict | None:
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        resp = requests.get(user_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.error("User fetch failed for %s: %s", platform, exc)
        return None


def _upsert_user(
    platform: str,
    user_info: dict,
    access_token: str,
    token_data: dict,
) -> User:
    platform_user_id = str(
        user_info.get("id")
        or user_info.get("uuid")
        or user_info.get("account_id")
        or ""
    )
    username = (
        user_info.get("login")
        or user_info.get("username")
        or user_info.get("nickname")
        or user_info.get("display_name")
        or ""
    )
    email = user_info.get("email") or ""
    name = user_info.get("name") or username
    avatar = (
        user_info.get("avatar_url")
        or (user_info.get("avatar_url") if platform == "github" else None)
        or (user_info.get("web_url") if platform == "gitlab" else None)
        or ""
    )

    # Find or create User
    pa = PlatformAccount.query.filter_by(
        platform=platform, platform_user_id=platform_user_id
    ).first()

    if pa:
        user = pa.user
    else:
        # Try to match by email
        user = User.query.filter_by(email=email).first() if email else None
        if not user:
            user = User(email=email or None, name=name, avatar_url=avatar)
            db.session.add(user)
            db.session.flush()

    # Upsert PlatformAccount
    if not pa:
        pa = PlatformAccount(
            user_id=user.id,
            platform=platform,
            platform_user_id=platform_user_id,
        )
        db.session.add(pa)

    pa.username = username
    pa.access_token = access_token
    pa.refresh_token = token_data.get("refresh_token")
    pa.avatar_url = avatar
    pa.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return user
