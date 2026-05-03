import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from app.services.pipeline_engine.chase_manager import ChaseDecisionEngine
from app.db.database import BotPipelineProcess

# Mocking utcnow to have full control over time-based tests
@pytest.fixture
def mock_now():
    return datetime(2026, 4, 9, 12, 0, 0)

@pytest.fixture
def mock_process(mock_now):
    process = MagicMock(spec=BotPipelineProcess)
    process.symbol = "BTC/USDT"
    process.side = "buy"
    process.amount = 0.1
    # Develoment note: use 10 seconds before mock_now as baseline
    process.created_at = mock_now - timedelta(seconds=10)
    process.updated_at = mock_now - timedelta(seconds=10)
    process.last_tick_price = 50000.0
    process.last_order_price = 50000.0
    process.status = "CHASING"
    return process

def test_should_update_cooldown_active(mock_process, mock_now):
    """Should NOT update if COOLDOWN_SECONDS (5s) has not passed."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        # Set last update to 2s ago
        mock_process.updated_at = mock_now - timedelta(seconds=2)
        
        # Even with a big price move, it should return False due to cooldown
        assert ChaseDecisionEngine.should_update(mock_process, 51000.0) is False
        
        # Test with custom cooldown (e.g. 1s) - now it SHOULD update
        assert ChaseDecisionEngine.should_update(mock_process, 51000.0, cooldown_seconds=1) is True

def test_should_update_cooldown_passed(mock_process, mock_now):
    """Should update if COOLDOWN_SECONDS (5s) has passed and price moved enough."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        # Set last update to 6s ago
        mock_process.updated_at = mock_now - timedelta(seconds=6)
        
        # Price move: 50100 vs 50000 (0.2% move > 0.05% threshold)
        assert ChaseDecisionEngine.should_update(mock_process, 50100.0) is True

def test_should_update_price_threshold_not_met(mock_process, mock_now):
    """Should NOT update if move is less than PRICE_DIFF_THRESHOLD (0.05%)."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        mock_process.updated_at = mock_now - timedelta(seconds=10)
        
        # Price move: 50010 vs 50000 (0.02% move < 0.05% threshold)
        assert ChaseDecisionEngine.should_update(mock_process, 50010.0) is False

def test_should_update_directional_buy_up(mock_process, mock_now):
    """BUY side: Should update if price is escaping upwards."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        mock_process.side = "buy"
        mock_process.updated_at = mock_now - timedelta(seconds=10)
        
        # Price moves UP (escaping): 50100
        assert ChaseDecisionEngine.should_update(mock_process, 50100.0) is True

def test_should_update_directional_buy_down(mock_process, mock_now):
    """BUY side: Should NOT update if price is moving downwards (better entry)."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        mock_process.side = "buy"
        mock_process.updated_at = mock_now - timedelta(seconds=10)
        
        # Price moves DOWN (better deal): 49900
        assert ChaseDecisionEngine.should_update(mock_process, 49900.0) is False

def test_should_update_directional_sell_down(mock_process, mock_now):
    """SELL side: Should update if price is escaping downwards."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        mock_process.side = "sell"
        mock_process.updated_at = mock_now - timedelta(seconds=10)
        
        # Price moves DOWN (escaping): 49900
        assert ChaseDecisionEngine.should_update(mock_process, 49900.0) is True

def test_should_update_directional_sell_up(mock_process, mock_now):
    """SELL side: Should NOT update if price is moving upwards (better entry)."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        mock_process.side = "sell"
        mock_process.updated_at = mock_now - timedelta(seconds=10)
        
        # Price moves UP (better deal): 50100
        assert ChaseDecisionEngine.should_update(mock_process, 50100.0) is False

def test_should_update_first_time(mock_process, mock_now):
    """Should always update on the first tick if last_tick_price is None."""
    with patch('app.services.pipeline_engine.chase_manager.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_now
        mock_process.last_tick_price = None
        mock_process.updated_at = mock_now - timedelta(seconds=10)
        
        assert ChaseDecisionEngine.should_update(mock_process, 50100.0) is True
