from sqlalchemy import (
    Column,
    String,
    Date,
    Numeric,
    Integer,
    PrimaryKeyConstraint,
)
from app.db.session import Base


class DailySummary(Base):
    __tablename__ = "daily_summary"

    ticker = Column(String, nullable=False)
    trading_date = Column(Date, nullable=False)

    open = Column(Numeric(18, 6), nullable=False)
    high = Column(Numeric(18, 6), nullable=False)
    low = Column(Numeric(18, 6), nullable=False)
    close = Column(Numeric(18, 6), nullable=False)

    range_pct = Column(Numeric(10, 6), nullable=False)

    low_bucket = Column(Integer, nullable=False)
    high_bucket = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("ticker", "trading_date", name="pk_daily_summary"),
    )
