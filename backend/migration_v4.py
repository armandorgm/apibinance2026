import sqlite3
import shutil
import os
from datetime import datetime

db_path = "binance_tracker_v3.db"
backup_path = f"{db_path}.bak_{int(datetime.now().timestamp())}"

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} no encontrado.")
        return

    print(f"[*] Creando backup en {backup_path}...")
    shutil.copy2(db_path, backup_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Identificar IDs de órdenes en fills que no existen en basic_orders
        print("[*] Identificando órdenes huérfanas...")
        cursor.execute("""
            SELECT DISTINCT order_id FROM fills 
            WHERE order_id NOT IN (SELECT id FROM basic_orders)
            AND order_id IS NOT NULL AND order_id != ''
        """)
        orphan_ids = [row[0] for row in cursor.fetchall()]
        
        if orphan_ids:
            print(f"[*] Sanando {len(orphan_ids)} órdenes huérfanas con registros esqueleto...")
            now_iso = datetime.utcnow().isoformat()
            for oid in orphan_ids:
                cursor.execute("""
                    INSERT INTO basic_orders (id, symbol, side, amount, price, status, datetime, originator, source, can_be_entry, is_bot_logged, order_type, created_at)
                    SELECT ?, symbol, side, 0, 0, 'FILLED', ?, 'MANUAL', 'STANDARD', 1, 0, 'UNKNOWN', ?
                    FROM fills WHERE order_id = ? LIMIT 1
                """, (oid, now_iso, now_iso, oid))

        # 2. Recrear basic_orders con la nueva columna parent_algo_id
        print("[*] Actualizando esquema de basic_orders...")
        cursor.execute("ALTER TABLE basic_orders RENAME TO basic_orders_old")
        cursor.execute("""
            CREATE TABLE basic_orders (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                datetime DATETIME NOT NULL,
                originator TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'STANDARD',
                can_be_entry BOOLEAN NOT NULL DEFAULT 1,
                is_bot_logged BOOLEAN NOT NULL DEFAULT 0,
                order_type TEXT NOT NULL DEFAULT 'LIMIT',
                parent_algo_id TEXT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (parent_algo_id) REFERENCES conditional_orders (id)
            )
        """)
        cursor.execute("CREATE INDEX idx_basic_orders_symbol ON basic_orders (symbol)")
        
        # Migrar datos (mapeando columnas)
        cursor.execute("""
            INSERT INTO basic_orders (id, symbol, side, amount, price, status, datetime, originator, source, can_be_entry, is_bot_logged, order_type, created_at)
            SELECT id, symbol, side, amount, price, status, datetime, originator, source, can_be_entry, is_bot_logged, order_type, created_at
            FROM basic_orders_old
        """)

        # 3. Recrear fills con el Foreign Key a basic_orders
        print("[*] Actualizando esquema de fills (añadiendo FK)...")
        cursor.execute("ALTER TABLE fills RENAME TO fills_old")
        cursor.execute("""
            CREATE TABLE fills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                fee REAL NOT NULL,
                fee_currency TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                datetime DATETIME NOT NULL,
                order_id TEXT NOT NULL,
                order_type TEXT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (order_id) REFERENCES basic_orders (id)
            )
        """)
        cursor.execute("CREATE INDEX idx_fills_trade_id ON fills (trade_id)")
        cursor.execute("CREATE INDEX idx_fills_symbol ON fills (symbol)")
        cursor.execute("CREATE INDEX idx_fills_order_id ON fills (order_id)")

        # Migrar datos
        cursor.execute("""
            INSERT INTO fills (id, trade_id, symbol, side, amount, price, cost, fee, fee_currency, timestamp, datetime, order_id, order_type, created_at)
            SELECT id, trade_id, symbol, side, amount, price, cost, fee, fee_currency, timestamp, datetime, order_id, order_type, created_at
            FROM fills_old
        """)

        # 4. Limpieza
        print("[*] Finalizando migración...")
        cursor.execute("DROP TABLE basic_orders_old")
        cursor.execute("DROP TABLE fills_old")
        
        conn.commit()
        print("[+] Migración completada con éxito.")

    except Exception as e:
        conn.rollback()
        print(f"[-] ERROR en la migración: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
