"""Health check endpoint."""
from flask import Blueprint, jsonify
from datetime import datetime, timezone

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "code-contribution-analyzer",
    })


@health_bp.get("/")
def root():
    return jsonify({
        "name": "Code Contribution Analyzer API",
        "version": "1.0.0",
        "docs": "/api/docs",
    })
