# Code Contribution Analyzer

> **A production-grade, full-stack tool for analyzing your coding contributions across GitHub, GitLab, and Bitbucket — with interactive charts, PDF/CSV/JSON reports, OAuth2 authentication, and a CLI.**

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![React](https://img.shields.io/badge/react-18-61dafb)
![TypeScript](https://img.shields.io/badge/typescript-5-3178c6)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Multi-Platform** | GitHub, GitLab, Bitbucket via OAuth2 |
| **Contribution Analytics** | Commits, additions, deletions, net LOC per repo & overall |
| **Language Breakdown** | 60+ languages detected; donut chart + table |
| **Activity Timeline** | Monthly additions/deletions area chart |
| **Top Repositories** | Ranked by your commit count; horizontal bar chart |
| **Report Export** | PDF (branded), CSV, and JSON downloads |
| **CLI Tool** | `cca analyze` — runs analyses from the terminal |
| **Secure OAuth** | Tokens stored encrypted; source code never leaves your machine |
| **Docker Ready** | One `docker compose up` to run the full stack |

---

## Architecture

```
code-contribution-analyzer/
├── src/
│   ├── api_clients/        # GitHub / GitLab / Bitbucket clients
│   ├── analysis/           # Language detection, line counting, contribution engine
│   ├── visualization/      # PDF, CSV, JSON report generators
│   ├── web/
│   │   ├── app.py          # Flask factory + SQLAlchemy models
│   │   └── routes/         # auth, analysis, repos, reports, health
│   ├── cli/                # Rich-powered CLI (click)
│   └── utils/              # Config, logging, rate limiter
├── frontend/               # React 18 + TypeScript + Tailwind + Recharts
│   └── src/
│       ├── pages/          # Dashboard, Analysis, Repositories, History, Settings
│       ├── components/     # Charts, StatCards, Layout, shared UI
│       ├── services/       # Axios API layer with auto token refresh
│       └── store/          # Zustand auth store (persisted)
├── tests/                  # pytest suite with ~85% coverage target
├── docker-compose.yml      # Full stack: API + Worker + Frontend + Nginx + DB + Redis
├── Dockerfile.api
└── frontend/Dockerfile.frontend
```

**Stack:**

| Layer | Technology |
|---|---|
| Backend | Flask 3, SQLAlchemy 2, Flask-JWT-Extended, Flask-Migrate |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7, Celery |
| Frontend | React 18, TypeScript, Tailwind CSS, Recharts, Zustand |
| Auth | OAuth2 (GitHub / GitLab / Bitbucket) + JWT |
| Reports | fpdf2, csv, json |
| Deployment | Docker Compose, Gunicorn, Nginx |

---

## Quick Start

### Option A — Docker Compose (recommended)

```bash
# 1. Clone
git clone https://github.com/stephenombuya/Code-Contribution-Analyzer
cd code-contribution-analyzer

# 2. Configure environment
cp .env.example .env
# Edit .env — add your OAuth app credentials (see "OAuth App Setup" below)

# 3. Start everything
docker compose up --build

# The app is now running at:
#   Frontend  →  http://localhost:80
#   API       →  http://localhost:5000
```

### Option B — Local Development

**Prerequisites:** Python 3.11+, Node 20+, PostgreSQL 16, Redis 7

```bash
# ── Backend ───────────────────────────────────────────────────────────────────
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your database URL and OAuth credentials

flask db upgrade          # run migrations
python src/main.py        # start API on :5000

# ── Frontend ──────────────────────────────────────────────────────────────────
cd frontend
npm install
npm run dev               # starts on :3000
```

---

## OAuth App Setup

You need to register an OAuth App on each platform you want to support.

### GitHub
1. Go to **Settings → Developer settings → OAuth Apps → New OAuth App**
2. Set **Authorization callback URL** to `http://localhost:3000/auth/callback/github`
3. Copy `Client ID` and `Client Secret` into `.env`:
   ```
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ```

### GitLab
1. Go to **User Settings → Applications → Add new application**
2. Scopes: `read_user read_api read_repository`
3. Redirect URI: `http://localhost:3000/auth/callback/gitlab`
4. Copy credentials to `.env`

### Bitbucket
1. Go to **Personal settings → OAuth → Add consumer**
2. Callback URL: `http://localhost:3000/auth/callback/bitbucket`
3. Permissions: `Account Read`, `Repositories Read`
4. Copy credentials to `.env`

---

## CLI Usage

```bash
# Install as a command
pip install -e .

# Analyze GitHub contributions
cca analyze --platform github --token ghp_yourtoken --username yourusername

# Save a PDF report
cca analyze --platform github --token ghp_yourtoken --output report.pdf

# Filter by date range
cca analyze --platform gitlab --token glpat_xxx --since 2024-01-01 --until 2024-12-31

# Check authenticated user
cca whoami --platform github --token ghp_yourtoken
```

Or run without installing:
```bash
python -m src.cli.cli_runner analyze --platform github --token ghp_xxx
```

---

## API Reference

All endpoints are under `/api/`.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/auth/authorize/:platform` | Get OAuth redirect URL |
| `POST` | `/api/auth/callback/:platform` | Exchange code for JWT |
| `POST` | `/api/auth/refresh` | Refresh access token |
| `GET` | `/api/auth/me` | Get current user |
| `DELETE` | `/api/auth/disconnect/:platform` | Disconnect a platform |

### Analysis
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analysis/run` | Run a new analysis |
| `GET` | `/api/analysis/` | List all analyses |
| `GET` | `/api/analysis/:id` | Get analysis by ID |
| `GET` | `/api/analysis/latest/:platform` | Latest completed analysis |
| `GET` | `/api/analysis/summary/all` | Aggregated cross-platform summary |
| `DELETE` | `/api/analysis/:id` | Delete an analysis |

### Repositories
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/repos/:platform` | List repositories |
| `GET` | `/api/repos/:platform/:owner/:repo` | Get single repo |

### Reports
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/reports/:id/json` | Download JSON report |
| `GET` | `/api/reports/:id/csv` | Download CSV report |
| `GET` | `/api/reports/:id/pdf` | Download PDF report |

---

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test class
pytest tests/test_all.py::TestLanguageDetector -v
```

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | Flask session secret | ✅ |
| `JWT_SECRET_KEY` | JWT signing key | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `GITHUB_CLIENT_ID` | GitHub OAuth app client ID | For GitHub |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app secret | For GitHub |
| `GITLAB_CLIENT_ID` | GitLab OAuth app client ID | For GitLab |
| `GITLAB_CLIENT_SECRET` | GitLab OAuth app secret | For GitLab |
| `BITBUCKET_CLIENT_ID` | Bitbucket OAuth consumer key | For Bitbucket |
| `BITBUCKET_CLIENT_SECRET` | Bitbucket OAuth consumer secret | For Bitbucket |
| `REDIS_URL` | Redis connection string | Optional (caching) |
| `FRONTEND_URL` | Frontend origin for CORS | ✅ |

See `.env.example` for a full template.

---

## Production Deployment

1. Set `FLASK_ENV=production` and strong secret keys in `.env`
2. Point `FRONTEND_URL` to your actual domain
3. Update OAuth app redirect URIs to your domain
4. Run `docker compose up -d`
5. For HTTPS: add your certificate to `certs/` and uncomment the HTTPS block in `nginx.conf`

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit: `git commit -m "feat: add my feature"`
4. Push and open a PR

---

## License

MIT — see [LICENSE](LICENSE).

---

**Developed with ❤️ by [Stephen Ombuya](https://github.com/stephenombuya)**
