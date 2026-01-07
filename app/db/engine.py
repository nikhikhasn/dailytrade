from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path
import os

from app.db.session import SessionLocal


def init_engine():
    # Find repo root explicitly
    engine_file = Path(__file__).resolve()
    repo_root = engine_file.parents[2]  # dailytrade/

    env_path = repo_root / ".env"

    print(f"🔍 Loading .env from: {env_path}")

    if not env_path.exists():
        raise RuntimeError(f".env file not found at {env_path}")

    load_dotenv(env_path)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required at application runtime")

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    SessionLocal.configure(bind=engine)
    return engine
