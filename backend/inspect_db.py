import sqlite3
import os

db_path = 'binance_tracker_v3.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} no existe")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tablas: {tables}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"Columnas en {table_name}: {[c[1] for c in columns]}")
    conn.close()
