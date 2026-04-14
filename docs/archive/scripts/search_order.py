import sqlite3
from datetime import datetime

DB_PATH = "backend/binance_tracker_v3.db"

def query_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = {}

    # Check basic_orders
    cursor.execute("SELECT * FROM basic_orders WHERE id = ?", (order_id,))
    results['basic_order'] = [dict(row) for row in cursor.fetchall()]

    # Check conditional_orders
    cursor.execute("SELECT * FROM conditional_orders WHERE id = ?", (order_id,))
    results['conditional_order'] = [dict(row) for row in cursor.fetchall()]

    # Check fills
    cursor.execute("SELECT * FROM fills WHERE order_id = ?", (order_id,))
    results['fills'] = [dict(row) for row in cursor.fetchall()]

    # Check trades
    cursor.execute("SELECT * FROM trades WHERE entry_order_id = ? OR exit_order_id = ?", (order_id, order_id))
    results['trades'] = [dict(row) for row in cursor.fetchall()]

    # Check ExchangeLog (optional search in parameters or response)
    # This might be slow if the table is huge, but worth a try with LIKE
    cursor.execute("SELECT * FROM exchange_logs WHERE parameters LIKE ? OR response LIKE ?", (f'%{order_id}%', f'%{order_id}%'))
    results['exchange_logs'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results

if __name__ == "__main__":
    order_id = "7378054921"
    res = query_order(order_id)
    
    print("--- BASIC ORDERS ---")
    if not res['basic_order']:
        print("Not found in basic_orders")
    for row in res['basic_order']:
        print(row)
    
    print("\n--- CONDITIONAL ORDERS ---")
    if not res['conditional_order']:
        print("Not found in conditional_orders")
    for row in res['conditional_order']:
        print(row)
        
    print("\n--- FILLS ---")
    if not res['fills']:
        print("Not found in fills")
    for row in res['fills']:
        print(row)

    print("\n--- MATCHED TRADES (PnL) ---")
    if not res['trades']:
        print("Not found in trades")
    for row in res['trades']:
        print(row)

    print("\n--- EXCHANGE LOGS ---")
    if not res['exchange_logs']:
        print("Not found in exchange_logs")
    for row in res['exchange_logs']:
        # Limit response/parameters length for brief output
        row['parameters'] = (row['parameters'][:100] + '...') if row['parameters'] and len(row['parameters']) > 100 else row['parameters']
        row['response'] = (row['response'][:100] + '...') if row['response'] and len(row['response']) > 100 else row['response']
        print(row)
