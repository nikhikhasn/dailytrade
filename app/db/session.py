from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.db.engine import engine


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)
