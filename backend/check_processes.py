from app.db.database import get_session_direct, BotPipelineProcess
with get_session_direct() as session:
    processes = session.query(BotPipelineProcess).all()
    print(f"Found {len(processes)} active/stored processes")
    for p in processes:
        print(f"ID: {p.id}, Symbol: {p.symbol}, Status: {p.status}, OrderID: {p.entry_order_id}")
