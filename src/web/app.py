"""
Flask application factory + SQLAlchemy models.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.utils.config_loader import get_config
from src.utils.logging_handler import setup_logging

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_override: dict | None = None) -> Flask:
    setup_logging(
        level=os.environ.get("LOG_LEVEL", "info"),
        log_file=os.environ.get("LOG_FILE"),
    )

    app = Flask(__name__, static_folder="static", template_folder="templates")
    cfg = get_config()
    app.config.from_object(cfg)
    cfg.ensure_dirs()

    if config_override:
        app.config.update(config_override)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
        supports_credentials=True,
    )

    # ── Blueprints ────────────────────────────────────────────────────────────
    from src.web.routes.auth import auth_bp
    from src.web.routes.analysis import analysis_bp
    from src.web.routes.repos import repos_bp
    from src.web.routes.reports import reports_bp
    from src.web.routes.health import health_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(repos_bp, url_prefix="/api/repos")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    return app


# ── Models ────────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    platform_accounts = db.relationship(
        "PlatformAccount", back_populates="user", cascade="all, delete-orphan"
    )
    analyses = db.relationship(
        "Analysis", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "platforms": [pa.platform for pa in self.platform_accounts],
        }


class PlatformAccount(db.Model):
    __tablename__ = "platform_accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False)  # github, gitlab, bitbucket
    platform_user_id = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True)
    profile_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    user = db.relationship("User", back_populates="platform_accounts")

    __table_args__ = (
        db.UniqueConstraint("platform", "platform_user_id", name="uq_platform_user"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "profile_url": self.profile_url,
        }


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    status = db.Column(
        db.String(50), nullable=False, default="pending"
    )  # pending | running | completed | failed
    since = db.Column(db.String(30), nullable=True)
    until = db.Column(db.String(30), nullable=True)
    result = db.Column(db.JSON, nullable=True)
    error = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="analyses")

    def to_dict(self, include_result: bool = False) -> dict:
        data = {
            "id": self.id,
            "platform": self.platform,
            "username": self.username,
            "status": self.status,
            "since": self.since,
            "until": self.until,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }
        if include_result and self.result:
            data["result"] = self.result
        return data


class CachedRepo(db.Model):
    __tablename__ = "cached_repos"

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    owner = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    cached_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("platform", "owner", "name", name="uq_cached_repo"),
    )
