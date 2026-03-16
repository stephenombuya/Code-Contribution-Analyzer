"""
Test suite for Code Contribution Analyzer.
Run with: pytest tests/ -v --cov=src
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock, patch

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    from src.web.app import create_app, db
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
        "SECRET_KEY": "test-secret",
        "FRONTEND_URL": "http://localhost:3000",
        "RATELIMIT_ENABLED": False,
    })
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Return JWT auth headers for a test user."""
    from src.web.app import db, User
    from flask_jwt_extended import create_access_token
    with app.app_context():
        user = User(email="test@example.com", name="Test User")
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))
        return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_check(self, client):
        rv = client.get("/health")
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["status"] == "ok"

    def test_root(self, client):
        rv = client.get("/")
        assert rv.status_code == 200
        data = rv.get_json()
        assert "name" in data


# ─────────────────────────────────────────────────────────────────────────────
# Language detector
# ─────────────────────────────────────────────────────────────────────────────

class TestLanguageDetector:
    def test_python_extension(self):
        from src.analysis.language_detector import detect_language
        assert detect_language("main.py") == "Python"
        assert detect_language("script.pyi") == "Python"

    def test_javascript(self):
        from src.analysis.language_detector import detect_language
        assert detect_language("app.js") == "JavaScript"
        assert detect_language("component.jsx") == "JavaScript"

    def test_typescript(self):
        from src.analysis.language_detector import detect_language
        assert detect_language("index.ts") == "TypeScript"
        assert detect_language("component.tsx") == "TypeScript"

    def test_unknown(self):
        from src.analysis.language_detector import detect_language
        assert detect_language("some.unknownext") is None

    def test_generated_files(self):
        from src.analysis.language_detector import is_generated
        assert is_generated("node_modules/lodash/index.js") is True
        assert is_generated("src/main.py") is False
        assert is_generated("dist/bundle.min.js") is True

    def test_docker(self):
        from src.analysis.language_detector import detect_language
        assert detect_language("Dockerfile") == "Dockerfile"


# ─────────────────────────────────────────────────────────────────────────────
# Line counter
# ─────────────────────────────────────────────────────────────────────────────

class TestLineCounter:
    def test_count_python_file(self, tmp_path):
        from src.analysis.line_counter import count_file
        f = tmp_path / "test.py"
        f.write_text("# comment\ndef foo():\n    pass\n\n")
        result = count_file(str(f))
        assert result is not None
        assert result.language == "Python"
        assert result.total_lines == 4
        assert result.comment_lines == 1
        assert result.blank_lines == 1

    def test_count_directory(self, tmp_path):
        from src.analysis.line_counter import count_directory
        (tmp_path / "a.py").write_text("x = 1\ny = 2\n")
        (tmp_path / "b.py").write_text("def f():\n    pass\n")
        result = count_directory(str(tmp_path))
        assert result.files_counted == 2
        assert result.total_lines == 4


# ─────────────────────────────────────────────────────────────────────────────
# Report generator
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_RESULT = {
    "platform": "github",
    "username": "testuser",
    "total_repos": 10,
    "total_commits": 500,
    "total_additions": 30000,
    "total_deletions": 5000,
    "net_lines": 25000,
    "languages": {"Python": 15000, "JavaScript": 8000, "TypeScript": 2000},
    "repos": [
        {
            "full_name": "testuser/repo-a",
            "language": "Python",
            "stars": 10,
            "forks": 2,
            "user_commits": 300,
            "user_additions": 20000,
            "user_deletions": 3000,
            "is_private": False,
        }
    ],
    "monthly_activity": [
        {"month": "2024-01", "commits": 50, "additions": 3000, "deletions": 500},
        {"month": "2024-02", "commits": 60, "additions": 3500, "deletions": 600},
    ],
    "top_repos": [],
}


class TestReportGenerator:
    def test_json_report(self):
        from src.visualization.report_generator import ReportGenerator
        gen = ReportGenerator(SAMPLE_RESULT, "testuser", "github")
        data = json.loads(gen.to_json())
        assert data["username"] == "testuser"
        assert data["summary"]["total_commits"] == 500
        assert "Python" in data["languages"]

    def test_csv_report(self):
        from src.visualization.report_generator import ReportGenerator
        gen = ReportGenerator(SAMPLE_RESULT, "testuser", "github")
        csv_bytes = gen.to_csv()
        text = csv_bytes.decode("utf-8")
        assert "testuser" in text
        assert "Python" in text
        assert "500" in text  # total_commits

    def test_pdf_report(self):
        from src.visualization.report_generator import ReportGenerator
        gen = ReportGenerator(SAMPLE_RESULT, "testuser", "github")
        pdf_bytes = gen.to_pdf()
        # PDF magic bytes
        assert pdf_bytes[:4] == b"%PDF"


# ─────────────────────────────────────────────────────────────────────────────
# API routes
# ─────────────────────────────────────────────────────────────────────────────

class TestAuthRoutes:
    def test_authorize_unknown_platform(self, client):
        rv = client.get("/api/auth/authorize/unknown")
        assert rv.status_code == 400

    def test_me_unauthenticated(self, client):
        rv = client.get("/api/auth/me")
        assert rv.status_code == 401

    def test_me_authenticated(self, client, app, auth_headers):
        with app.app_context():
            rv = client.get("/api/auth/me", headers=auth_headers)
            assert rv.status_code == 200
            data = rv.get_json()
            assert data["email"] == "test@example.com"


class TestAnalysisRoutes:
    def test_list_unauthenticated(self, client):
        rv = client.get("/api/analysis/")
        assert rv.status_code == 401

    def test_list_empty(self, client, app, auth_headers):
        with app.app_context():
            rv = client.get("/api/analysis/", headers=auth_headers)
            assert rv.status_code == 200
            data = rv.get_json()
            assert data["analyses"] == []
            assert data["total"] == 0

    def test_run_missing_platform(self, client, app, auth_headers):
        with app.app_context():
            rv = client.post("/api/analysis/run", json={}, headers=auth_headers)
            assert rv.status_code == 400

    def test_run_no_connected_account(self, client, app, auth_headers):
        with app.app_context():
            rv = client.post(
                "/api/analysis/run",
                json={"platform": "github"},
                headers=auth_headers,
            )
            assert rv.status_code == 403


class TestReposRoutes:
    def test_list_unauthenticated(self, client):
        rv = client.get("/api/repos/github")
        assert rv.status_code == 401

    def test_list_not_connected(self, client, app, auth_headers):
        with app.app_context():
            rv = client.get("/api/repos/github", headers=auth_headers)
            assert rv.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Contribution analyzer (mocked client)
# ─────────────────────────────────────────────────────────────────────────────

class TestContributionAnalyzer:
    def _make_mock_client(self):
        client = MagicMock()
        client.platform = "github"
        client.list_repositories.return_value = [
            {
                "full_name": "user/repo-a",
                "name": "repo-a",
                "description": "Test repo",
                "language": "Python",
                "stargazers_count": 5,
                "forks_count": 1,
                "private": False,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "clone_url": "https://github.com/user/repo-a.git",
                "namespace": {"path": "user"},
                "path": "repo-a",
            }
        ]
        client.list_commits.return_value = [
            {
                "sha": "abc123",
                "commit": {
                    "author": {"date": "2024-01-15T10:00:00Z"},
                    "message": "Add feature",
                },
                "stats": {"additions": 100, "deletions": 20, "total": 120},
            }
        ]
        client.get_repository_languages.return_value = {"Python": 5000, "Shell": 200}
        return client

    def test_analyze_returns_summary(self):
        from src.analysis.contribution_analyzer import ContributionAnalyzer
        from src.api_clients.github_client import GitHubClient
        client = self._make_mock_client()
        # Patch isinstance check
        with patch.object(GitHubClient, "__instancecheck__", return_value=True):
            analyzer = ContributionAnalyzer(client, "user")
            summary = analyzer.analyze(max_repos=1)

        assert summary.username == "user"
        assert summary.platform == "github"
        assert summary.total_repos == 1
        assert summary.total_commits == 1

    def test_empty_repos(self):
        from src.analysis.contribution_analyzer import ContributionAnalyzer
        client = MagicMock()
        client.platform = "github"
        client.list_repositories.return_value = []
        analyzer = ContributionAnalyzer(client, "user")
        summary = analyzer.analyze()
        assert summary.total_repos == 0
        assert summary.total_commits == 0
