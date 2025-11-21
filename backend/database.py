from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "notes.db"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def _ensure_schema() -> None:
    """Add missing columns when an older SQLite file is present.

    SQLite ignores new columns when the table already exists. Because we don't
    run a migration framework here, we opportunistically add the PARA-related
    fields when they're missing so the API doesn't 500 on inserts.
    """

    inspector = inspect(engine)
    if not inspector.has_table("notes"):
        return

    existing_columns = {col["name"] for col in inspector.get_columns("notes")}
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))

        def add_column(name: str, ddl: str) -> None:
            if name not in existing_columns:
                conn.execute(text(f"ALTER TABLE notes ADD COLUMN {ddl}"))

        add_column("para_bucket", "VARCHAR(50) NOT NULL DEFAULT 'resource'")
        add_column("area_name", "VARCHAR(255)")
        add_column("project_outcome", "TEXT")
        add_column("classification_confidence", "FLOAT")
        add_column("classified_by", "VARCHAR(50)")
        add_column("user_overridden", "BOOLEAN NOT NULL DEFAULT 0")
        add_column("original_para_bucket", "VARCHAR(50)")
        add_column("updated_at", "DATETIME DEFAULT (CURRENT_TIMESTAMP)")
        add_column("captured_from", "VARCHAR(255)")

        conn.execute(text("PRAGMA foreign_keys=ON"))


_ensure_schema()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
