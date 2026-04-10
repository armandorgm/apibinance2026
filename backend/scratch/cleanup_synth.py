import asyncio
import os
import sys
# Add backend to path
sys.path.append(os.getcwd())

from app.db.database import engine, Fill, Trade
from sqlmodel import Session, select, delete

async def cleanup_synthetic():
    target_id_part = "7378054921"
    
    with Session(engine) as session:
        # 1. Find and delete Fills
        # The synthetic order ID usually starts with CSYNTH_
        stmt_fills = select(Fill).where(Fill.order_id.like(f"%{target_id_part}%"), Fill.order_id.like("%SYNTH%"))
        fills_to_delete = session.exec(stmt_fills).all()
        
        print(f"[CLEANUP] Found {len(fills_to_delete)} synthetic fills.")
        for f in fills_to_delete:
            print(f"  - Deleting Fill: {f.trade_id} (Order: {f.order_id})")
            session.delete(f)
            
        # 2. Find and delete Trades
        # We look for trades where entry or exit order ID matches the synthetic one
        stmt_trades = select(Trade).where(
            (Trade.entry_order_id.like(f"%{target_id_part}%") & Trade.entry_order_id.like("%SYNTH%")) |
            (Trade.exit_order_id.like(f"%{target_id_part}%") & Trade.exit_order_id.like("%SYNTH%"))
        )
        trades_to_delete = session.exec(stmt_trades).all()
        
        print(f"[CLEANUP] Found {len(trades_to_delete)} synthetic trades.")
        for t in trades_to_delete:
            print(f"  - Deleting Trade: {t.id} ({t.symbol} {t.entry_side}->{t.exit_side})")
            session.delete(t)
            
        session.commit()
        print("[CLEANUP] Done.")

if __name__ == "__main__":
    asyncio.run(cleanup_synthetic())
