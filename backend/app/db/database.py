"""
Database models and session management using SQLModel.
"""
from sqlmodel import SQLModel, Session, create_engine, Field
from typing import Optional
from datetime import datetime
from app.core.config import settings
from contextlib import contextmanager


class Fill(SQLModel, table=True):
    """
    Raw execution (fill) from Binance.
    Stores each individual trade execution.
    """
    __tablename__ = "fills"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trade_id: str = Field(index=True, unique=True)  # Binance trade ID
    symbol: str = Field(index=True)
    side: str  # 'buy' or 'sell'
    amount: float
    price: float
    cost: float  # amount * price
    fee: float  # Commission paid
    fee_currency: str
    timestamp: int  # Unix timestamp in milliseconds
    datetime: datetime
    order_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Trade(SQLModel, table=True):
    """
    Processed trade (matched buy/sell pair).
    Represents a complete round-trip trade.
    """
    __tablename__ = "trades"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    entry_side: str  # 'buy' or 'sell'
    entry_price: float
    entry_amount: float
    entry_fee: float
    entry_timestamp: int
    entry_datetime: datetime
    exit_side: str
    exit_price: float
    exit_amount: float
    exit_fee: float
    exit_timestamp: int
    exit_datetime: datetime
    pnl_net: float  # Net PnL after fees
    pnl_percentage: float
    duration_seconds: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    """Get database session context manager."""
    with Session(engine) as session:
        yield session


def get_session_direct():
    """Get database session directly."""
    return Session(engine)
