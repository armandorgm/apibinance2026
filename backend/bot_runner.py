"""
Standalone script to run the Trading Bot independently from the FastAPI backend.
Reads configuration from the BotConfig table and runs the strategy loop.
"""
import asyncio
import sys
import os

# Add the current directory to sys.path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import create_db_and_tables, Session, engine, BotConfig
from app.services.bot_service import bot_instance
from sqlmodel import select

async def run_bot():
    print("--- Starting Independent Trading Bot ---")
    
    # Ensure tables exist
    create_db_and_tables()
    
    # Check if bot is enabled in DB
    enabled = False
    with Session(engine) as session:
        statement = select(BotConfig)
        config = session.exec(statement).first()
        if config and config.is_enabled:
            enabled = True
    
    # Start the bot instance
    # Even if disabled in DB initially, TradingBot internal loop 
    # will check config.is_enabled on every iteration.
    await bot_instance.start()
    
    # Keep the script alive
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("--- Stopping Bot ---")
        await bot_instance.stop()

if __name__ == "__main__":
    asyncio.run(run_bot())
