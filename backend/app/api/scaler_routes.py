"""
Scaler Bot API Routes — /api/scaler
====================================
Endpoints para controlar el ScheduledScalerBot (Bot C).

  POST /api/scaler/enable   — Habilita el bot para un símbolo.
  POST /api/scaler/disable  — Deshabilita el bot.
  GET  /api/scaler/status   — Estado actual del bot.

Implementado: 2026-04-25 | AI Agent — apibinance2026
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("apibinance2026")

router = APIRouter(prefix="/api/scaler", tags=["Scaler Bot"])


class ScalerEnableRequest(BaseModel):
    symbol: str = Field(..., example="1000PEPE/USDC:USDC")
    default_profit_pc: float = Field(
        default=0.005,
        ge=0.001,
        description="Fallback profit % when no open TP is found. Min 0.001 (0.1%).",
    )
    interval_hours: float = Field(
        default=8.0,
        ge=0.5,
        description="Execution interval in hours. Min 0.5h.",
    )


@router.post("/enable")
async def enable_scaler(body: ScalerEnableRequest):
    """
    Enables the ScheduledScalerBot for the given symbol.

    - Side is inferred dynamically each cycle (position + nearest TP agreement).
    - The first cycle executes immediately upon enable.
    - State is persisted in DB and survives backend restarts.
    """
    from app.services.scheduled_scaler_bot import scheduled_scaler_bot

    try:
        status = await scheduled_scaler_bot.enable(
            symbol=body.symbol,
            default_profit_pc=body.default_profit_pc,
            interval_hours=body.interval_hours,
        )
        logger.info(
            f"[SCALER API] Enabled for {body.symbol} | "
            f"interval={body.interval_hours}h | profit_pc={body.default_profit_pc}"
        )
        return {
            "message": f"ScheduledScalerBot enabled for {body.symbol}.",
            "status": status,
        }
    except Exception as e:
        logger.error(f"[SCALER API] Enable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable")
async def disable_scaler():
    """
    Disables the ScheduledScalerBot.
    The running loop exits within 60 seconds (interrupt window).
    State is persisted as disabled in DB.
    """
    from app.services.scheduled_scaler_bot import scheduled_scaler_bot

    try:
        status = await scheduled_scaler_bot.disable()
        logger.info("[SCALER API] Disabled by user request.")
        return {
            "message": "ScheduledScalerBot disabled.",
            "status": status,
        }
    except Exception as e:
        logger.error(f"[SCALER API] Disable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_scaler_status():
    """
    Returns the current in-memory status of the ScheduledScalerBot.
    Includes: is_enabled, symbol, default_profit_pc, interval_hours, loop_running.
    For persisted stats (cycles_executed, last_execution_at), query the DB directly
    or use the /api/scaler/stats endpoint.
    """
    from app.services.scheduled_scaler_bot import scheduled_scaler_bot
    from app.db.database import ScalerBotConfig, get_session_direct
    from sqlmodel import select

    live = scheduled_scaler_bot.get_status()

    # Enrich with DB stats
    db_stats = {}
    try:
        with get_session_direct() as session:
            row = session.exec(
                select(ScalerBotConfig).where(
                    ScalerBotConfig.symbol == scheduled_scaler_bot.symbol
                )
            ).first()
            if row:
                db_stats = {
                    "cycles_executed": row.cycles_executed,
                    "last_execution_at": row.last_execution_at.isoformat()
                    if row.last_execution_at else None,
                    "last_cycle_side": row.last_cycle_side,
                    "last_profit_pc_used": row.last_profit_pc_used,
                }
    except Exception as e:
        logger.warning(f"[SCALER API] Could not read DB stats: {e}")

    return {**live, **db_stats}
