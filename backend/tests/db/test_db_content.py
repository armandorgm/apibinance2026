import asyncio
from sqlmodel import select
from app.db.database import get_session_direct
from app.db.database import Fill

async def check_fills():
    print("Checking Fills in Database...")
    with get_session_direct() as session:
        statement = select(Fill).order_by(Fill.timestamp.desc()).limit(5)
        results = session.exec(statement).all()
        
        for f in results:
            print(f"Fill ID: {f.trade_id}, Order ID: |{f.order_id}|, Symbol: {f.symbol}, Datetime: {f.datetime}")

if __name__ == "__main__":
    asyncio.run(check_fills())
