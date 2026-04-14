import sqlite3
import os

db_path = "f:/apibinance2026/backend/data/trading_bot.db" # Standard path usually
# Let's check where the db is from config
from app.core.config import settings
db_uri = settings.DATABASE_URL
if db_uri.startswith("sqlite:///"):
    db_path = db_uri.replace("sqlite:///", "")

print(f"Checking database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(bot_pipeline_processes)")
    columns = cursor.fetchall()
    print("Columns in bot_pipeline_processes:")
    for col in columns:
        print(col)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
