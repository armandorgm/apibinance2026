"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Binance API credentials
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./binance_tracker.db"
    
    # CORS - stored as comma-separated string, converted to list via property
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Exchange settings
    EXCHANGE_NAME: str = "binance"
    TESTNET: bool = False
    
    # Bot settings
    BOT_ENABLED: bool = False
    BOT_SYMBOL: str = "BTC/USDT"
    BOT_INTERVAL: int = 60 # seconds
    
    def get_cors_origins(self) -> List[str]:
        """
        Parse CORS_ORIGINS from comma-separated string.
        Returns list of origins.
        """
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return origins if origins else ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
