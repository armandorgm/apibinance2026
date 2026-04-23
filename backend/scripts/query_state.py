from app.db.database import get_session_direct, BotSignal, BotPipelineProcess
import contextlib

with get_session_direct() as session:
    print("--- SIGNALS ---")
    signals = session.query(BotSignal).order_by(BotSignal.id.desc()).limit(20).all()
    for s in signals:
        print(f"Signal: {s.rule_triggered} | Action: {s.action_taken} | Success: {s.success}")
    
    print("\n--- PROCESSES ---")
    processes = session.query(BotPipelineProcess).order_by(BotPipelineProcess.id.desc()).limit(5).all()
    for p in processes:
        print(f"Process {p.id}: {p.symbol} | Status: {p.status} | Sub: {p.sub_status} | Entry: {p.entry_order_id}")
