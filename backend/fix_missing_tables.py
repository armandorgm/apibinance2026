from app.db.database import create_db_and_tables
import asyncio

if __name__ == "__main__":
    print("Verificando/Creando tablas de base de datos...")
    create_db_and_tables()
    print("Tablas verificadas.")
