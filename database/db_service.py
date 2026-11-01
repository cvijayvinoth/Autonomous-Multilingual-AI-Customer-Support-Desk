"""Database service operations."""

import os
from pathlib import Path
from database.models import Ticket, KBDeficiency, init_db

db_dir = Path(__file__).resolve().parent
db_dir.mkdir(parents=True, exist_ok=True)

db_url = os.getenv("DATABASE_URL", f"sqlite:///{db_dir / 'support_desk.db'}")
SessionLocal = init_db(db_url)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
