import asyncio
import logging
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.getcwd())

from app.db.database import Session, engine, BotPipelineProcess
from app.core.exchange import exchange_manager
from app.services.pipeline_engine.registry import ACTIONS
from sqlmodel import select

# Configure logging
logging.basicConfig(level=logging.INFO)

async def force_advance():
    print("--- [ARCHITECT] Starting Force Advance Script (v5 - Final Pull) ---")
    with Session(engine) as session:
        procs = session.exec(select(BotPipelineProcess).filter(BotPipelineProcess.status == "CHASING")).all()
        if not procs:
            print("[ARCHITECT] No active CHASING processes found.")
            return

        for p in procs:
            print(f"[ARCHITECT] Checking Process {p.id} | Symbol: {p.symbol} | OrderID: {p.entry_order_id}")
            try:
                # 1. Fetch from Binance
                order_info = await exchange_manager.fetch_order_raw(p.symbol, p.entry_order_id)
                status = order_info.get("status")
                print(f"[ARCHITECT] Binance Status: {status}")
                
                if status == "closed":
                    print(f"[ARCHITECT] Order is FILLED. Using Registry Handler...")
                    handler_key = "ADAPTIVE_OTO_V2" if "NATIVE" in (p.sub_status or "") else "ADAPTIVE_OTO"
                    handler = ACTIONS.get(handler_key)
                    
                    if handler:
                        print(f"[ARCHITECT] Calling {handler_key}.handle_fill with profit_pc=0.001...")
                        # This calls the FIXED code in native_actions.py
                        await handler.handle_fill(p, session, profit_pc=0.001)
                        
                        session.refresh(p)
                        print(f"[ARCHITECT] Post-fill Status: {p.status} | Sub: {p.sub_status}")
                    else:
                        print(f"[ARCHITECT] Error: Handler {handler_key} not found.")
                else:
                    print(f"[ARCHITECT] Order is still {status}. No action taken.")
                    
            except Exception as e:
                print(f"[ARCHITECT] Error processing {p.id}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_advance())
