"""
Reactor Routes — REST control interface for CloseFillReactor (Bot B).
Registered in main.py under /api/reactor prefix.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.close_fill_reactor import close_fill_reactor
from app.services.chase_v2_service import chase_v2_service
from app.core.logger import logger
from app.core.exchange import exchange_manager

router = APIRouter()


class ReactorEnableRequest(BaseModel):
    symbol: str
    side: str           # 'buy' or 'sell'
    amount: float       # position size in USDC
    profit_pc: float = 0.005  # Default: 0.5% — range [0.001, 0.10]


@router.post("/enable", response_model=Dict[str, Any])
async def enable_reactor(req: ReactorEnableRequest):
    """
    Activa el CloseFillReactor (Bot B) y arranca inmediatamente el primer Chase (Bot A).

    Body params:
      - symbol    : par a operar (e.g. '1000PEPE/USDC')
      - side      : 'buy' o 'sell'
      - amount    : monto en USDC de la posición
      - profit_pc : TP % para cada ciclo. Rango: 0.001–0.10. Default 0.005 (0.5%)
    """
    try:
        if not (0.001 <= req.profit_pc <= 0.10):
            raise HTTPException(
                status_code=422,
                detail=f"profit_pc must be between 0.001 (0.1%) and 0.10 (10%). Got: {req.profit_pc}",
            )
        if req.side.lower() not in ("buy", "sell"):
            raise HTTPException(status_code=422, detail="side must be 'buy' or 'sell'")
        if req.amount <= 0:
            raise HTTPException(status_code=422, detail="amount must be greater than 0")

        normalized_symbol = await exchange_manager.normalize_symbol(req.symbol)

        # 1. Enable Bot B reactor (stores params for all subsequent follow-up cycles)
        close_fill_reactor.enable(
            symbol=normalized_symbol,
            side=req.side.lower(),
            amount=req.amount,
            profit_pc=req.profit_pc,
        )

        # 2. Start first Chase (Bot A) immediately
        logger.info(f"[API/REACTOR] Launching initial Chase for {normalized_symbol}...")
        chase_result = await chase_v2_service.init_chase(
            symbol=normalized_symbol,
            side=req.side.lower(),
            amount=req.amount,
            profit_pc=req.profit_pc,
        )

        if not chase_result.get("success"):
            # Rollback: disable reactor if Bot A failed to start
            close_fill_reactor.disable()
            raise HTTPException(
                status_code=400,
                detail=f"Bot B enabled but Bot A failed to start: {chase_result.get('error')}",
            )

        return {
            "success": True,
            "message": f"Bot B enabled + Bot A started for {normalized_symbol} | TP={req.profit_pc*100:.2f}%",
            "chase": chase_result,
            "reactor": close_fill_reactor.get_status(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API/REACTOR] Error enabling reactor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable", response_model=Dict[str, Any])
async def disable_reactor():
    """
    Deactivates the CloseFillReactor (Bot B) and cancels any pending follow-up task.
    """
    try:
        close_fill_reactor.disable()
        return {
            "success": True,
            "message": "Reactor disabled.",
            "status": close_fill_reactor.get_status(),
        }
    except Exception as e:
        logger.error(f"[API/REACTOR] Error disabling reactor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
def get_reactor_status():
    """
    Returns the current observable state of the CloseFillReactor (Bot B).
    Includes: enabled flag, target symbol, last cooldown, cycle count.
    """
    try:
        return {
            "success": True,
            "reactor": close_fill_reactor.get_status(),
        }
    except Exception as e:
        logger.error(f"[API/REACTOR] Error getting status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
