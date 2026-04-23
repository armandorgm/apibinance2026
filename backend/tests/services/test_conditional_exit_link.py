"""Tests de cruce entrada ↔ CONDITIONAL por createTime."""
from types import SimpleNamespace

from app.services.conditional_exit_link import (
    aggregate_conditional_orders_by_create_time,
    cross_entry_timestamp_with_conditional_orders,
    filter_conditional_algo_orders,
    order_closes_entry_position,
)


def _order(**kw):
    return SimpleNamespace(**kw)


def test_filter_conditional_algo_orders():
    orders = [
        _order(algo_type="CONDITIONAL", id="1"),
        _order(algo_type="VP", id="2"),
        _order(algo_type=None, id="3"),
    ]
    f = filter_conditional_algo_orders(orders)
    assert len(f) == 1 and f[0].id == "1"


def test_cross_same_create_time_and_closes_long():
    ts = 1_713_456_789_000
    o = _order(
        id="a1",
        algo_type="CONDITIONAL",
        create_time_ms=ts,
        closes_long=True,
        closes_short=False,
        conditional_kind="take_profit",
    )
    by_ts = aggregate_conditional_orders_by_create_time([o])
    linked = cross_entry_timestamp_with_conditional_orders(ts, by_ts, "buy")
    assert len(linked) == 1
    assert linked[0].id == "a1"


def test_cross_rejects_wrong_close_side():
    ts = 99
    o = _order(
        id="x",
        algo_type="CONDITIONAL",
        create_time_ms=ts,
        closes_long=False,
        closes_short=True,
        conditional_kind="take_profit",
    )
    by_ts = aggregate_conditional_orders_by_create_time([o])
    linked = cross_entry_timestamp_with_conditional_orders(ts, by_ts, "buy")
    assert linked == []


def test_order_closes_entry_position():
    assert order_closes_entry_position("buy", _order(closes_long=True, closes_short=False)) is True
    assert order_closes_entry_position("sell", _order(closes_long=False, closes_short=True)) is True
