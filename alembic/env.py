from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from dotenv import load_dotenv
from pathlib import Path
import os

# ------------------------------------------------------------------
# Load environment variables (robust for Alembic)
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

config = context.config

# ------------------------------------------------------------------
# DATABASE URL (with safe fallback for Alembic)
# ------------------------------------------------------------------
db_url = os.getenv("DATABASE_URL")

if not db_url:
    db_url = "postgresql+psycopg://dailytrade:dailytrade@localhost:5432/dailytrade"
    print("⚠️ Alembic using fallback DATABASE_URL")

config.set_main_option("sqlalchemy.url", db_url)

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------------
# Metadata (IMPORTANT for autogenerate)
# TODdo : update this everytime a new column is added
# ------------------------------------------------------------------
from app.db.session import Base
from app.db import models        # minute_bars
from app.db import models_daily # daily_summary

target_metadata = Base.metadata

# ------------------------------------------------------------------
# Migration runners
# ------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
