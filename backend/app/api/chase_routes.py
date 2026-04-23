from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.db.database import get_session, BotPipelineProcess
from app.services.chase_v2_service import chase_v2_service
from app.core.logger import logger
from sqlalchemy.orm import Session

router = APIRouter()

class ChaseInitRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    profit_pc: float = 0.005
    pipeline_id: int = 0

class ChaseStopRequest(BaseModel):
    process_id: int

@router.post("/init", response_model=Dict[str, Any])
async def init_chase(req: ChaseInitRequest):
    """Starts the autonomous Chase V2 process."""
    try:
        res = await chase_v2_service.init_chase(
            symbol=req.symbol,
            side=req.side.lower(),
            amount=req.amount,
            profit_pc=req.profit_pc,
            pipeline_id=req.pipeline_id
        )
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error", "Failed to start Chase V2"))
        return res
    except Exception as e:
        logger.error(f"[API] Error in init_chase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=Dict[str, Any])
async def stop_chase(req: ChaseStopRequest):
    """Manually stops an active chase process."""
    try:
        success = await chase_v2_service.stop_chase(req.process_id)
        if not success:
            raise HTTPException(status_code=404, detail="Process not found or not active")
        return {"success": True, "message": f"Process {req.process_id} stopped successfully"}
    except Exception as e:
        logger.error(f"[API] Error in stop_chase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=Dict[str, Any])
def get_chase_status(symbol: Optional[str] = None):
    """Gets the status of active chase processes."""
    try:
        with get_session() as session:
            query = session.query(BotPipelineProcess).filter(
                BotPipelineProcess.status == "CHASING"
            )
            if symbol:
                query = query.filter(BotPipelineProcess.symbol == symbol)
                
            processes = query.all()
        
        result = []
        for p in processes:
            result.append({
                "id": p.id,
                "symbol": p.symbol,
                "side": p.side,
                "amount": p.amount,
                "entry_order_id": p.entry_order_id,
                "sub_status": p.sub_status,
                "last_order_price": p.last_order_price,
                "last_tick_price": p.last_tick_price,
                "created_at": p.created_at,
                "updated_at": p.updated_at
            })
            
        return {"success": True, "active_processes": result}
    except Exception as e:
        logger.error(f"[API] Error in get_chase_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
