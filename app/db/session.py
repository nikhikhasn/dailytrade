from sqlalchemy.orm import sessionmaker, DeclarativeBase

# IMPORTANT:
# This file must NOT create an engine at import time.
# Alembic only needs Base.metadata.

class Base(DeclarativeBase):
    pass

# SessionLocal will be bound later at runtime (not during import)
SessionLocal = sessionmaker()
