from app.db.database import create_db_and_tables, SQLModel, engine
from app.core.config import settings
import os

try:
    print(f"URL de base de datos en settings: {settings.DATABASE_URL}")
    print(f"URL del engine en database.py: {engine.url}")
    print("Tablas detectadas en metadata:", list(SQLModel.metadata.tables.keys()))
    print("Iniciando creación de base de datos...")
    create_db_and_tables()
    print("Éxito!")
    
    # Extraer nombre del archivo de la URL
    db_file = settings.DATABASE_URL.split('/')[-1]
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f"Archivo {db_file} creado. Tamaño: {size} bytes")
except Exception as e:
    import traceback
    traceback.print_exc()
