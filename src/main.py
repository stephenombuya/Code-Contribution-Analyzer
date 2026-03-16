"""
Application entry point.
Run with: python src/main.py  (dev)
          gunicorn "src.main:app"  (prod)
"""
import os
from src.web.app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )
