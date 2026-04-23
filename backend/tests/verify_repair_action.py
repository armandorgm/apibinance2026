
import asyncio
import os
import sys
# Add backend to path
sys.path.append(os.getcwd())

from sqlmodel import Session, select
from app.db.database import engine, Fill, Trade
from app.services.repair_service import RepairService

async def verify_repair():
    print("--- [VERIFY] Testing Repair Logic ---")
    order_id = "7378054921"
    profit_pc = 0.5
    
    try:
        # 1. Preview
        print(f"[VERIFY] Fetching preview for ID {order_id}...")
        preview = RepairService.get_repair_preview(order_id, profit_pc)
        print(f"[VERIFY] Target Buy Price: {preview['target_buy_price']}")
        
        # 2. Execute
        print(f"[VERIFY] Executing repair...")
        result = RepairService.execute_repair(order_id, profit_pc)
        print(f"[VERIFY] Result: {result}")
        
        # 3. Check matched trade
        with Session(engine) as session:
            stmt = select(Trade).where(Trade.symbol == preview['symbol']).order_by(Trade.created_at.desc()).limit(1)
            last_trade = session.exec(stmt).first()
            if last_trade:
                print(f"[VERIFY] New Trade Found: ID {last_trade.id}")
                print(f"[VERIFY] PnL Net: {last_trade.pnl_net}")
                print(f"[VERIFY] PnL %: {last_trade.pnl_percentage}")
                
                # Check if matches profit_pc roughly (considering fees)
                if abs(last_trade.pnl_percentage - profit_pc) < 0.1:
                    print("[VERIFY] SUCCESS: PnL percentage is within expected range.")
                else:
                    print(f"[VERIFY] WARNING: PnL percentage {last_trade.pnl_percentage} differs from target {profit_pc}")
            else:
                print("[VERIFY] FAILED: No trade was created.")
                
    except Exception as e:
        print(f"[VERIFY] ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_repair())
