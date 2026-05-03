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
   # Unified Binance Futures Tracker Dashboard (V5.9.24 - Stabilized)
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

from app.api.chase_routes import router as chase_router
app.include_router(chase_router, prefix="/api/chase", tags=["chase"])

from app.api.reactor_routes import router as reactor_router
app.include_router(reactor_router, prefix="/api/reactor", tags=["reactor"])

from app.api.scaler_routes import router as scaler_router
app.include_router(scaler_router)  # prefix defined inside scaler_routes: /api/scaler


# WebSocket Notifications Endpoint
from fastapi import WebSocket, WebSocketDisconnect
from app.services.notification_service import notification_manager

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    conn_id = await notification_manager.connect(websocket)
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=20)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # No messages from client, but we keep the socket alive
                # by simply continuing the loop.
                pass
    except WebSocketDisconnect:
        notification_manager.disconnect(conn_id)
    except Exception as e:
        logger.error(f"[WS] Critical error for {conn_id}: {e}")
        notification_manager.disconnect(conn_id)

@app.on_event("startup")
async def startup_event():
    # Bot and Stream Manager must run in the same process for efficient WebSocket broadcasting
    from app.services.bot_service import bot_instance
    if settings.BOT_ENABLED:
        asyncio.create_task(bot_instance.start())

    # Restore ScheduledScalerBot state from DB (survives restarts)
    from app.services.scheduled_scaler_bot import scheduled_scaler_bot
    restored = await scheduled_scaler_bot.load_from_db()
    if restored:
        logger.info("[STARTUP] ScheduledScalerBot state restored from DB.")


@app.on_event("shutdown")
async def shutdown_event():
    """Global cleanup of resources to prevent unclosed sessions Warnings (V5.9.23)."""
    logger.info("[SHUTDOWN] Starting cleanup...")
    from app.services.bot_service import bot_instance
    from app.core.exchange import exchange_manager
    
    # 1. Stop Bot & Stream Service
    await bot_instance.stop()
    
    # 2. Close CCXT sessions
    await exchange_manager.close()
    
    logger.info("[SHUTDOWN] Cleanup complete.")

@app.get("/")
async def root():
    return {"message": "Binance Futures Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
