
from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("PRAGMA journal_mode"))
    mode = result.scalar()
    print(f"Current journal mode: {mode}")

    result = conn.execute(text("PRAGMA synchronous"))
    sync = result.scalar()
    print(f"Current synchronous setting: {sync}")
