from app.db.database import ReactorConfig, get_session_direct
from sqlmodel import select

def check_reactor_db():
    with get_session_direct() as session:
        config = session.get(ReactorConfig, 1)
        if config:
            print(f"ID: {config.id}")
            print(f"Is Enabled: {config.is_enabled}")
            print(f"Symbol: {config.symbol}")
            print(f"Side: {config.side}")
            print(f"Amount: {config.amount}")
            print(f"Profit %: {config.profit_pc}")
            print(f"Updated At: {config.updated_at}")
        else:
            print("No ReactorConfig found with ID 1")

if __name__ == "__main__":
    check_reactor_db()
