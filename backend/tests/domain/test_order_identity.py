import pytest
from datetime import datetime
from app.db.database import OrderSource, Originator
from app.domain.orders.standard_order import StandardOrder
from app.domain.orders.algo_order import AlgoOrder

def test_standard_order_identity_prefix():
    """Verifica que StandardOrder inyecta el prefijo 'B'."""
    raw_id = "123456789"
    order = StandardOrder(
        order_id=raw_id,
        symbol="BTC/USDT",
        side="buy",
        amount=1.0,
        price=50000.0,
        status="FILLED",
        dt=datetime.now(),
        originator=Originator.MANUAL,
        is_bot_logged=False
    )
    
    assert order.raw_id == raw_id, "El raw_id debe ser fiel al ID original"
    assert order.id == f"B{raw_id}", "El id debe tener el prefijo 'B' según el Glosario"
    assert order.to_dict()["id"] == f"B{raw_id}"
    assert order.to_dict()["raw_id"] == raw_id

def test_algo_order_identity_prefix():
    """Verifica que AlgoOrder inyecta el prefijo 'C'."""
    raw_id = "algo_9999"
    order = AlgoOrder(
        order_id=raw_id,
        symbol="BTC/USDT",
        side="sell",
        amount=0.5,
        price=55000.0,
        status="NEW",
        dt=datetime.now(),
        originator=Originator.AUTO,
        is_bot_logged=True,
        conditional_kind="stop_loss"
    )
    
    assert order.raw_id == raw_id, "El raw_id debe ser fiel al ID original del Algo Service"
    assert order.id == f"C{raw_id}", "El id debe tener el prefijo 'C' según el Glosario"
    assert order.to_dict()["id"] == f"C{raw_id}"

def test_id_prefixing_protection():
    """Verifica que no se duplique el prefijo si ya existe."""
    raw_id = "B555"
    order = StandardOrder(
        order_id=raw_id,
        symbol="BTC/USDT",
        side="buy",
        amount=1.0,
        price=50000.0,
        status="FILLED",
        dt=datetime.now(),
        originator=Originator.MANUAL
    )
    assert order.id == "B555", "No debe quedar como BB555"
