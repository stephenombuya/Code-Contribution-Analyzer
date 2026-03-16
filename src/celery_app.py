"""
Celery application factory.
Usage: celery -A src.celery_app worker --loglevel=info
"""
from __future__ import annotations

from celery import Celery
from src.web.app import create_app

flask_app = create_app()


def make_celery(app) -> Celery:
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(flask_app)


# ── Async analysis task ────────────────────────────────────────────────────────

@celery.task(bind=True, name="run_analysis")
def run_analysis_task(
    self,
    analysis_id: int,
    platform: str,
    username: str,
    access_token: str,
    since: str | None = None,
    until: str | None = None,
    max_repos: int = 50,
    include_private: bool = True,
) -> dict:
    """Background task for long-running analyses."""
    from datetime import datetime, timezone
    from src.web.app import db, Analysis
    from src.api_clients.github_client import GitHubClient
    from src.api_clients.gitlab_client import GitLabClient
    from src.api_clients.bitbucket_client import BitbucketClient
    from src.analysis.contribution_analyzer import ContributionAnalyzer

    clients = {
        "github": GitHubClient,
        "gitlab": GitLabClient,
        "bitbucket": BitbucketClient,
    }

    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return {"error": "Analysis not found"}

    try:
        analysis.status = "running"
        analysis.started_at = datetime.now(timezone.utc)
        db.session.commit()

        client = clients[platform](access_token)
        analyzer = ContributionAnalyzer(client, username)
        summary = analyzer.analyze(
            since=since,
            until=until,
            max_repos=max_repos,
            include_private=include_private,
        )

        analysis.result = summary.to_dict()
        analysis.status = "completed"
        analysis.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        return summary.to_dict()

    except Exception as exc:
        analysis.status = "failed"
        analysis.error = str(exc)
        analysis.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        raise
