from sqlmodel import Session, select, func
from app.db.database import engine, Trade, Fill, BotPipeline, BotConfig, Order

def check_db():
    with Session(engine) as s:
        try:
            print(f"--- DB STATUS ---")
            print(f"Trades: {s.exec(select(func.count(Trade.id))).one()}")
            print(f"Fills: {s.exec(select(func.count(Fill.id))).one()}")
            print(f"Pipelines: {s.exec(select(func.count(BotPipeline.id))).one()}")
            print(f"Orders: {s.exec(select(func.count(Order.id))).one()}")
            
            config = s.exec(select(BotConfig)).all()
            print(f"BotConfigs: {len(config)}")
        except Exception as e:
            print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_db()
