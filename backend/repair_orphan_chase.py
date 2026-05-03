import asyncio
import os
import sys
# Add backend to path
sys.path.append(os.getcwd())

from sqlmodel import Session, select
from app.db.database import engine, BotPipelineProcess, BotSignal, Fill, Trade, BotConfig
from app.core.exchange import exchange_manager

async def repair_and_normalize():
    print("--- [REPAIR] Starting Symbol Normalization and Orphan Cleanup ---")
    
    with Session(engine) as session:
        # 1. Cleanup Orphan PEPE (Process ID 1)
        # The user reported ID 1 was stuck in CHASING for PEPE
        pepe_orphan = session.get(BotPipelineProcess, 1)
        if pepe_orphan:
            print(f"[REPAIR] Found orphan process for {pepe_orphan.symbol} (ID: {pepe_orphan.id}). Deleting...")
            session.delete(pepe_orphan)
            session.commit()
            print("[REPAIR] Orphan process deleted.")
        else:
            print("[REPAIR] Orphan process ID 1 not found.")

        # 2. Normalize Symbols in all relevant tables
        # Tables to check: BotPipelineProcess, BotSignal, Fill, Trade, BotConfig
        
        # Helper to normalize all records in a table
        async def normalize_table(model_class):
            records = session.exec(select(model_class)).all()
            total_updated = 0
            for r in records:
                old_symbol = r.symbol
                new_symbol = await exchange_manager.normalize_symbol(old_symbol)
                if old_symbol != new_symbol:
                    print(f"[REPAIR] Normalizing {model_class.__name__} {r.id}: {old_symbol} -> {new_symbol}")
                    r.symbol = new_symbol
                    total_updated += 1
            if total_updated > 0:
                session.commit()
                print(f"[REPAIR] Updated {total_updated} records in {model_class.__name__}")
            else:
                print(f"[REPAIR] No changes needed for {model_class.__name__}")

        print("\n--- Normalizing Tables ---")
        await normalize_table(BotPipelineProcess)
        await normalize_table(BotSignal)
        await normalize_table(Fill)
        await normalize_table(Trade)
        await normalize_table(BotConfig)

    print("\n--- [REPAIR] Finished ---")

if __name__ == "__main__":
    asyncio.run(repair_and_normalize())
