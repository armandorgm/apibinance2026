import pytest
from sqlmodel import SQLModel, create_engine, Session
from app.db.database import get_session_direct
import app.db.database as db_module

@pytest.fixture(name="session", scope="function")
def session_fixture():
    """
    Crea una base de datos SQLite en memoria para cada test,
    garantizando aislamiento total y limpieza.
    """
    # Usamos sqlite:///:memory: para máxima velocidad y limpieza
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # Creamos todas las tablas (BasicOrder, ConditionalOrder, Fill, Trade, etc.)
    SQLModel.metadata.create_all(test_engine)
    
    # Monkeypatch del engine global y la función de sesión
    old_engine = db_module.engine
    db_module.engine = test_engine
    
    # Redefinimos get_session_direct para los tests
    def mock_get_session_direct():
        return Session(test_engine)
    
    old_get_session_direct = db_module.get_session_direct
    db_module.get_session_direct = mock_get_session_direct
    
    with Session(test_engine) as session:
        yield session
    
    # Restauramos el estado original después del test (limpieza de parches)
    db_module.engine = old_engine
    db_module.get_session_direct = old_get_session_direct
