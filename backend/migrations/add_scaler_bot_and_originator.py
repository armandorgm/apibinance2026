"""
Migration: Add originator to bot_pipeline_processes + create scaler_bot_config table.
Run once after pulling this branch.

Usage:
    cd backend
    python migrations/add_scaler_bot_and_originator.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from app.core.config import settings

# Extract file path from sqlite:///./xxx.db
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
print(f"[MIGRATION] Target DB: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# ─── 1. Add 'originator' column to bot_pipeline_processes ────────────────────
try:
    cur.execute(
        "ALTER TABLE bot_pipeline_processes ADD COLUMN originator TEXT DEFAULT NULL"
    )
    print("[MIGRATION] OK Added 'originator' column to bot_pipeline_processes")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("[MIGRATION] WARN Column 'originator' already exists -- skipping.")
    else:
        raise

# --- 2. Create scaler_bot_config table (if not exists) ---
cur.execute("""
CREATE TABLE IF NOT EXISTS scaler_bot_config (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol           TEXT    NOT NULL UNIQUE,
    is_enabled       INTEGER NOT NULL DEFAULT 0,
    default_profit_pc REAL   NOT NULL DEFAULT 0.005,
    interval_hours   REAL    NOT NULL DEFAULT 8.0,
    cycles_executed  INTEGER NOT NULL DEFAULT 0,
    last_execution_at TEXT   DEFAULT NULL,
    last_cycle_side  TEXT    DEFAULT NULL,
    last_profit_pc_used REAL DEFAULT NULL,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
)
""")
print("[MIGRATION] OK Table 'scaler_bot_config' ensured.")

# --- 3. Index on scaler_bot_config.symbol ---
cur.execute("""
CREATE INDEX IF NOT EXISTS ix_scaler_bot_config_symbol ON scaler_bot_config (symbol)
""")
print("[MIGRATION] OK Index on scaler_bot_config.symbol ensured.")

# --- 4. Index on bot_pipeline_processes.originator ---
cur.execute("""
CREATE INDEX IF NOT EXISTS ix_bot_pipeline_processes_originator
ON bot_pipeline_processes (originator)
""")
print("[MIGRATION] OK Index on bot_pipeline_processes.originator ensured.")

conn.commit()
conn.close()
print("[MIGRATION] DONE Migration complete. No data was deleted.")

