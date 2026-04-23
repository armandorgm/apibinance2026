import pytest
from datetime import datetime
from sqlmodel import select
from app.db.database import BasicOrder, ConditionalOrder, Fill, Originator, OrderSource

def test_fill_can_point_to_different_order_tables(session):
    """
    Valida la Integridad Referencial Polimórfica (Glosario).
    Un Fill debe poder guardar un order_id que pertenezca a cualquiera de las dos tablas físicas.
    """
    # 1. Creamos una Orden Básica
    b_order = BasicOrder(
        id="B_123", symbol="BTC/USDT", side="buy", amount=1.0, price=50000.0,
        status="FILLED", datetime=datetime.now(), originator=Originator.MANUAL
    )
    session.add(b_order)
    
    # 2. Creamos una Orden Condicional
    c_order = ConditionalOrder(
        id="C_456", symbol="BTC/USDT", side="buy", amount=1.0, price=50000.0,
        status="FILLED", datetime=datetime.now(), originator=Originator.AUTO
    )
    session.add(c_order)
    
    # 3. Creamos Fills que apuntan a ambas (usamos IDs crudos en la lógica real, 
    # pero aquí probamos que el campo order_id en Fill no tiene restricción física)
    f1 = Fill(
        trade_id="t1", symbol="BTC/USDT", side="buy", amount=1.0, price=50000.0,
        cost=50000.0, fee=50.0, fee_currency="USDT", timestamp=1000, 
        datetime=datetime.now(), order_id="B_123"
    )
    f2 = Fill(
        trade_id="t2", symbol="BTC/USDT", side="buy", amount=1.0, price=50000.0,
        cost=50000.0, fee=50.0, fee_currency="USDT", timestamp=2000, 
        datetime=datetime.now(), order_id="C_456"
    )
    session.add(f1)
    session.add(f2)
    session.commit()
    
    # 4. Verificación: Recuperar y comprobar
    fills = session.exec(select(Fill)).all()
    assert len(fills) == 2
    
    # Comprobar que podemos encontrar el "padre" en tablas distintas
    fill_to_basic = session.exec(select(Fill).where(Fill.order_id == "B_123")).first()
    fill_to_cond = session.exec(select(Fill).where(Fill.order_id == "C_456")).first()
    
    assert session.exec(select(BasicOrder).where(BasicOrder.id == fill_to_basic.order_id)).first() is not None
    assert session.exec(select(ConditionalOrder).where(ConditionalOrder.id == fill_to_cond.order_id)).first() is not None

def test_segmented_id_uniqueness(session):
    """Verifica que podemos tener el mismo ID numérico en tablas distintas sin colisión."""
    # Binance podría teóricamente usar el mismo ID para un algoOrder y un standardOrder en servicios distintos
    id_comun = "777777"
    
    b_order = BasicOrder(
        id=id_comun, symbol="BTC/USDT", side="buy", amount=1.0, price=50000.0,
        status="FILLED", datetime=datetime.now(), originator=Originator.MANUAL
    )
    c_order = ConditionalOrder(
        id=id_comun, symbol="BTC/USDT", side="sell", amount=1.0, price=51000.0,
        status="FILLED", datetime=datetime.now(), originator=Originator.AUTO
    )
    
    session.add(b_order)
    session.add(c_order)
    session.commit()
    
    assert session.exec(select(BasicOrder).where(BasicOrder.id == id_comun)).first().side == "buy"
    assert session.exec(select(ConditionalOrder).where(ConditionalOrder.id == id_comun)).first().side == "sell"
