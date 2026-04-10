# Reload trigger: 2026-04-09 13:28:00
"""
FastAPI application for automated trading dashboard.
"""
"""
FastAPI main application entry point.
Handles API routes, CORS, and application configuration.
"""
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.core.logger import logger

# Initialize database on startup
create_db_and_tables()

app = FastAPI(
    title="Binance Futures Tracker API",
    description="API para rastrear y calcular PnL de operaciones en Binance Futures",
    version="1.0.0"
)

# Configure CORS to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Bot is now decoupled and runs via bot_runner.py
    # from app.services.bot_service import bot_instance
    # if settings.BOT_ENABLED:
    #     asyncio.create_task(bot_instance.start())
    pass

@app.on_event("shutdown")
async def shutdown_event():
    from app.services.bot_service import bot_instance
    await bot_instance.stop()

@app.get("/")
async def root():
    return {"message": "Binance Futures Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
