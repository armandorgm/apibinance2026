"""
Database models and session management using SQLModel.
"""
from sqlmodel import SQLModel, Session, create_engine, Field, select
from typing import Optional
from datetime import datetime
from app.core.config import settings
from contextlib import contextmanager


from contextlib import contextmanager
from enum import Enum

class Originator(str, Enum):
    BOT = "BOT_APP"
    MANUAL = "MANUAL"
    AUTO = "AUTO_ALGO"

class OrderSource(str, Enum):
    STANDARD = "STANDARD"
    ALGO = "ALGO"

class BasicOrder(SQLModel, table=True):
    """
    Standard Binance Order (LIMIT/MARKET).
    Faithful source from CCXT's fetch_order.
    """
    __tablename__ = "basic_orders"
    
    id: str = Field(primary_key=True)  # Raw Binance orderId
    symbol: str = Field(index=True)
    side: str  # 'buy' or 'sell'
    amount: float
    price: float
    status: str
    datetime: datetime
    originator: Originator
    source: OrderSource = Field(default=OrderSource.STANDARD)
    can_be_entry: bool = True
    is_bot_logged: bool = False
    order_type: str = "LIMIT"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConditionalOrder(SQLModel, table=True):
    """
    Binance Algo Service Order (TP/SL/Trailing).
    Faithful source from Binance Algo API.
    """
    __tablename__ = "conditional_orders"
    
    id: str = Field(primary_key=True)  # Raw Binance algoId
    symbol: str = Field(index=True)
    side: str
    amount: float
    price: float
    status: str
    datetime: datetime
    originator: Originator
    source: OrderSource = Field(default=OrderSource.ALGO)
    can_be_entry: bool = False
    is_bot_logged: bool = False
    order_type: str = "STOP_MARKET"
    create_time_ms: Optional[int] = None
    conditional_kind: Optional[str] = None # take_profit, stop_loss, trailing
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    order_id: str = Field(index=True) # ID crudo (se busca en basic o conditional via app logic)
    order_type: Optional[str] = None # Standard type (LIMIT/MARKET)
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
    # Metadatos de órdenes (precisión desde fills + Binance)
    entry_order_id: Optional[str] = None
    exit_order_id: Optional[str] = None
    entry_order_type: Optional[str] = None
    exit_order_type: Optional[str] = None


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


class BotPipeline(SQLModel, table=True):
    """
    User-defined sequence of conditions and actions (Pipelines).
    Supports Open/Closed extension via JSON configuration.
    """
    __tablename__ = "bot_pipelines"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    symbol: str = Field(index=True)
    is_active: bool = Field(default=True)
    trigger_event: str = Field(default="POLLING") # POLLING, ON_TICK, etc.
    pipeline_config: str = Field(default="{}") # JSON string containing the Nodes/Steps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BotPipelineProcess(SQLModel, table=True):
    """
    State tracking for active pipeline executions like Adaptive OTO Scaling.
    Cleaned up automatically once the final order is placed.
    """
    __tablename__ = "bot_pipeline_processes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pipeline_id: int = Field(index=True)
    symbol: str = Field(index=True)
    
    # Mother order tracking
    entry_order_id: Optional[str] = None
    side: str = Field(default="buy")
    amount: float = Field(default=0.0)
    
    # Prices to determine when to move
    last_tick_price: Optional[float] = None # Price of market when we decided to move
    last_order_price: Optional[float] = None # Price truly sent to Binance
    
    # Status of the session: 'CHASING', 'WAITING_FILL', 'COMPLETED', 'ABORTED'
    status: str = Field(default="CHASING")
    
    # Custom chasing parameters (Overriding defaults)
    custom_cooldown: Optional[int] = None
    custom_threshold: Optional[float] = None
    retry_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExchangeLog(SQLModel, table=True):
    """
    Global log for all raw exchange requests and responses.
    """
    __tablename__ = "exchange_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    method: str = Field(index=True)
    parameters: Optional[str] = None
    response: Optional[str] = None
    is_error: bool = Field(default=False)
    error_message: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)

def create_db_and_tables():
    """Create database tables from scratch (Fresh Start)."""
    # Simply create tables. No legacy migrations needed since DB is new.
    SQLModel.metadata.create_all(engine)
    
    # Initialize default bot config if none exists
    with Session(engine) as session:
        statement = select(BotConfig)
        config = session.exec(statement).first()
        if not config:
            print("[DB] Initializing default BotConfig...")
            new_config = BotConfig(
                symbol="1000PEPEUSDC", # Updated default per user request
                interval=60,
                is_enabled=False,
                trade_amount=5.01
            )
            session.add(new_config)
            session.commit()
    print("[DB] New schema created successfully")



@contextmanager
def get_session():
    """Get database session context manager."""
    with Session(engine) as session:
        yield session


def get_session_direct():
    """Get database session directly."""
    return Session(engine)
