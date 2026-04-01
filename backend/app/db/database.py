"""
Database models and session management using SQLModel.
"""
from sqlmodel import SQLModel, Session, create_engine, Field, select
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


class BotSignal(SQLModel, table=True):
    """
    Log of a strategy engine evaluation.
    Tracks what rules were evaluated and if action was taken.
    """
    __tablename__ = "bot_signals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    rule_triggered: Optional[str] = None
    action_taken: Optional[str] = None # 'NEW_ORDER', 'UPDATE_RANGE', or None
    params_snapshot: Optional[str] = None # JSON snapshot of parameters used
    
    # New fields for exchange interaction
    exchange_request: Optional[str] = None # JSON string of request sent to exchange
    exchange_response: Optional[str] = None # JSON string of response from exchange
    
    success: bool = True
    error_message: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BotConfig(SQLModel, table=True):
    """
    Dynamic configuration for the trading bot.
    """
    __tablename__ = "bot_config"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(default="BTC/USDT")
    interval: int = Field(default=60)
    is_enabled: bool = Field(default=False)
    trade_amount: float = Field(default=5.01)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)
    
    # Simple migration for bot_signals (adds new columns if they don't exist)
    import sqlite3
    from app.core.config import settings
    # Extract path from sqlite:///./path.db
    db_name = settings.DATABASE_URL.replace("sqlite:///", "").replace("./", "")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Check current columns in bot_signals
        cursor.execute("PRAGMA table_info(bot_signals);")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add columns if they are missing
        if "exchange_request" not in columns:
            cursor.execute("ALTER TABLE bot_signals ADD COLUMN exchange_request TEXT;")
        if "exchange_response" not in columns:
            cursor.execute("ALTER TABLE bot_signals ADD COLUMN exchange_response TEXT;")
            
        # Check current columns in bot_config
        cursor.execute("PRAGMA table_info(bot_config);")
        config_columns = [col[1] for col in cursor.fetchall()]
        
        # Add columns if they are missing
        if "trade_amount" not in config_columns:
            cursor.execute("ALTER TABLE bot_config ADD COLUMN trade_amount FLOAT DEFAULT 5.01;")
            
        conn.commit()
        conn.close()
        print("[DB] Applied migrations successfully")
    except Exception as e:
        print(f"[DB] Migration check skipped or failed: {e}")
    
    # Initialize default bot config if none exists
    with Session(engine) as session:
        statement = select(BotConfig)
        config = session.exec(statement).first()
        if not config:
            print("[DB] Initializing default BotConfig...")
            new_config = BotConfig(
                symbol="BTC/USDT",
                interval=60,
                is_enabled=False
            )
            session.add(new_config)
            session.commit()


@contextmanager
def get_session():
    """Get database session context manager."""
    with Session(engine) as session:
        yield session


def get_session_direct():
    """Get database session directly."""
    return Session(engine)
