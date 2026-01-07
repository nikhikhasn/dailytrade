from sqlalchemy import (
    Column,
    String,
    DateTime,
    Numeric,
    BigInteger,
    Index,
    PrimaryKeyConstraint,
)
from app.db.session import Base


class MinuteBar(Base):
    __tablename__ = "minute_bars"

    ticker = Column(String, nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)

    open = Column(Numeric(18, 6), nullable=False)
    high = Column(Numeric(18, 6), nullable=False)
    low = Column(Numeric(18, 6), nullable=False)
    close = Column(Numeric(18, 6), nullable=False)

    volume = Column(BigInteger, nullable=False)

    __table_args__ = (
        # Composite primary key (REQUIRED)
        PrimaryKeyConstraint("ticker", "ts", name="pk_minute_bars"),
        Index("ix_minute_bars_ticker_ts", "ticker", "ts"),
    )
