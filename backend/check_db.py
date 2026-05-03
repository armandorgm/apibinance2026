from app.db.database import get_session, ScalerBotConfig
from sqlmodel import select
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.getcwd())

with get_session() as session:
    configs = session.exec(select(ScalerBotConfig)).all()
    print(f"Total configs: {len(configs)}")
    for c in configs:
        print(f"Symbol: {c.symbol}, Enabled: {c.is_enabled}, Last Execution: {c.last_execution_at}")
