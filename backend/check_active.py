import asyncio
from app.db.database import Session, engine, BotPipelineProcess
from sqlmodel import select

def check_db():
    with Session(engine) as session:
        procs = session.exec(select(BotPipelineProcess).filter(BotPipelineProcess.status == "CHASING")).all()
        for p in procs:
            print(f"ID: {p.id} | Symbol: {p.symbol} | OrderID: {p.entry_order_id} | Status: {p.status} | Sub: {p.sub_status}")

if __name__ == "__main__":
    check_db()
