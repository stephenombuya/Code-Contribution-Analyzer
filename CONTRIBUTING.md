# Contributing to Code Contribution Analyzer

Thank you for your interest in contributing! Please follow these guidelines.

## Development Setup

```bash
git clone https://github.com/stephenombuya/Code-Contribution-Analyzer
cd code-contribution-analyzer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Code Style

- **Python**: Black (line length 99) + flake8. Run `black src/ tests/` before committing.
- **TypeScript/React**: ESLint config in `frontend/`. Run `npm run lint`.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add GitLab language breakdown
fix: handle missing commit stats
docs: update README setup steps
test: add rate limiter unit tests
refactor: extract OAuth helper function
```

## Pull Request Process

1. Fork the repo and create a branch from `main`.
2. Add tests for any new functionality.
3. Ensure `pytest tests/ -v` passes with no failures.
4. Update `README.md` if you've changed API endpoints or config.
5. Open a PR with a clear description of what changed and why.

## Reporting Bugs

Please open a GitHub issue with:
- Steps to reproduce
- Expected vs actual behaviour
- Relevant logs or error messages
- Your OS and Python/Node version

## Code of Conduct

All contributors are expected to uphold a respectful, professional standard of interaction. Harassment, trolling, or abusive language will result in immediate removal.
