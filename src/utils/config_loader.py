"""
Configuration loader — reads from environment variables / .env file.
All application config flows through here.
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (won't override already-set env vars)
load_dotenv()


def _required(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise EnvironmentError(f"Required environment variable '{key}' is not set.")
    return val


def _optional(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


class Config:
    # ── Core ──────────────────────────────────────────────────────────────────
    ENV: str = _optional("FLASK_ENV", "production")
    DEBUG: bool = _optional("FLASK_DEBUG", "false").lower() == "true"
    SECRET_KEY: str = _optional("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY: str = _optional("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    FRONTEND_URL: str = _optional("FRONTEND_URL", "http://localhost:3000")

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = _optional(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/code_analyzer"
    )
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = _optional("REDIS_URL", "redis://localhost:6379/0")

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES: int = 2592000  # 30 days

    # ── GitHub ────────────────────────────────────────────────────────────────
    GITHUB_CLIENT_ID: str = _optional("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: str = _optional("GITHUB_CLIENT_SECRET")
    GITHUB_API_TOKEN: str = _optional("GITHUB_API_TOKEN")
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_OAUTH_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token"

    # ── GitLab ────────────────────────────────────────────────────────────────
    GITLAB_CLIENT_ID: str = _optional("GITLAB_CLIENT_ID")
    GITLAB_CLIENT_SECRET: str = _optional("GITLAB_CLIENT_SECRET")
    GITLAB_BASE_URL: str = _optional("GITLAB_BASE_URL", "https://gitlab.com")
    GITLAB_API_BASE: str = f"{_optional('GITLAB_BASE_URL', 'https://gitlab.com')}/api/v4"

    # ── Bitbucket ─────────────────────────────────────────────────────────────
    BITBUCKET_CLIENT_ID: str = _optional("BITBUCKET_CLIENT_ID")
    BITBUCKET_CLIENT_SECRET: str = _optional("BITBUCKET_CLIENT_SECRET")
    BITBUCKET_API_BASE: str = "https://api.bitbucket.org/2.0"

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = _optional("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = _optional(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/2"
    )

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATELIMIT_DEFAULT: str = _optional("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_STORAGE_URL: str = _optional(
        "RATELIMIT_STORAGE_URL", "redis://localhost:6379/3"
    )

    # ── Storage ───────────────────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = Path(_optional("DATA_DIR", str(BASE_DIR / "data")))
    REPOS_DIR: Path = Path(_optional("REPOS_DIR", str(BASE_DIR / "data" / "repos")))
    REPORTS_DIR: Path = Path(
        _optional("REPORTS_DIR", str(BASE_DIR / "data" / "reports"))
    )

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.REPOS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_URL = "sqlite:///:memory:"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


_configs = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config() -> type[Config]:
    env = os.environ.get("FLASK_ENV", "production")
    return _configs.get(env, ProductionConfig)
