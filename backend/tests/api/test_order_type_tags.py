from app.services.order_type_tags import (
    extract_binance_order_type_from_ccxt_order,
    tags_from_binance_order_type,
)


def test_tags_take_profit_market():
    t = tags_from_binance_order_type("TAKE_PROFIT_MARKET")
    assert "TAKE_PROFIT" in t
    assert "MARKET" in t


def test_tags_conditional_algo():
    t = tags_from_binance_order_type("TAKE_PROFIT_MARKET", algo_type="CONDITIONAL")
    assert "CONDITIONAL" in t


def test_extract_from_ccxt_info_orig_type():
    raw = {"info": {"origType": "LIMIT"}, "type": "limit"}
    assert extract_binance_order_type_from_ccxt_order(raw) == "LIMIT"
