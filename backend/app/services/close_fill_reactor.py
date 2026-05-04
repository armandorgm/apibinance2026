"""
CloseFillReactor — Bot B (Reactive Follow-Up System)

Designed by AI Agent — 2026-04-24
Responsibility: Single, isolated reactor that observes Chase V2 completions
and autonomously triggers follow-up chases with a dynamic cooldown.

SOLID compliance:
  - S: Dedicated only to reacting on fill events. No placement or tracking logic.
  - O: New behaviors (e.g. different cooldown strategies) extend, not modify.
  - D: Lazy imports break circular dependency with ChaseV2Service.

V5.9.48 — Reactor Resilience & Persistence:
  - Fixed symbol mismatch using Market ID comparison (e.g. 1000PEPE/USDC:USDC vs 1000PEPE/USDC).
  - Eliminated auto-disable on transient Bot A failure (rollback removed in reactor_routes).
  - _delayed_chase now retries once (after 30s) if init_chase fails transiently.
  - Added save_to_db() / load_from_db() for state persistence across backend restarts.
  - V5.9.45: Symbol normalization via exchange_manager in on_position_closed.
  - V5.9.44: DetachedInstanceError fix using plain primitive arguments.

Flow:
  ChaseV2Service.handle_fill()
    └─> asyncio.create_task(
            reactor.on_position_closed(symbol=process.symbol,
                                        created_at=process.created_at))
          └─> asyncio.sleep(cooldown)
                └─> chase_v2_service.init_chase(...)
"""

import asyncio
from datetime import datetime
from typing import Optional

from app.core.logger import logger


class CloseFillReactor:
    """
    Singleton reactor that monitors Chase V2 completions (via async hook)
    and launches a follow-up Chase after a cooldown = 50% of the closed cycle duration.
    """

    _instance: Optional["CloseFillReactor"] = None

    def __new__(cls) -> "CloseFillReactor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.is_enabled: bool = False
        self.enabled_symbol: Optional[str] = None
        self.side: str = "buy"                     # Configured at enable-time
        self.amount: float = 0.0                   # Configured at enable-time
        self.profit_pc: float = 0.005              # Configured at enable-time
        self.last_cooldown_seconds: float = 0.0
        self.last_cycle_duration_seconds: float = 0.0
        self.cycles_triggered: int = 0
        self._pending_task: Optional[asyncio.Task] = None
        self._initialized = True
        logger.info("[REACTOR] CloseFillReactor initialized.")

    # ─────────────────────────────────────────────────────────────
    # Public control interface (consumed by reactor_routes.py)
    # ─────────────────────────────────────────────────────────────

    def enable(self, symbol: str, side: str = "buy", amount: float = 0.0, profit_pc: float = 0.005) -> None:
        """Activates the reactor with fixed parameters used for every follow-up cycle."""
        self.is_enabled = True
        self.enabled_symbol = symbol
        self.side = side
        self.amount = amount
        self.profit_pc = profit_pc
        self.cycles_triggered = 0
        logger.info(
            f"[REACTOR] Enabled — symbol: {symbol} | side: {side} | "
            f"amount: {amount} | TP: {profit_pc*100:.2f}%"
        )
        # V5.9.46: Persist state so backend restarts don't lose configuration
        self._save_to_db()

    def disable(self) -> None:
        """Deactivates the reactor and cancels any pending follow-up task."""
        self.is_enabled = False
        if self._pending_task and not self._pending_task.done():
            self._pending_task.cancel()
            logger.info("[REACTOR] Pending follow-up task cancelled.")
        logger.info("[REACTOR] Disabled.")
        # V5.9.46: Persist disabled state to DB
        self._save_to_db()

    def get_status(self) -> dict:
        """Returns the current observable state of the reactor."""
        return {
            "is_enabled": self.is_enabled,
            "symbol": self.enabled_symbol,
            "side": self.side,
            "amount": self.amount,
            "profit_pc": self.profit_pc,
            "profit_pc_pct": f"{self.profit_pc * 100:.2f}%",
            "last_cooldown_seconds": self.last_cooldown_seconds,
            "last_cycle_duration_seconds": self.last_cycle_duration_seconds,
            "cycles_triggered": self.cycles_triggered,
            "pending_task_active": (
                self._pending_task is not None and not self._pending_task.done()
            ),
        }

    # ─────────────────────────────────────────────────────────────
    # Persistence interface (V5.9.46)
    # ─────────────────────────────────────────────────────────────

    def _save_to_db(self) -> None:
        """
        Persists current reactor state to the DB (upsert on id=1).
        Called automatically by enable() and disable().
        Fire-and-forget — errors are logged, never raised.
        """
        try:
            from app.db.database import ReactorConfig, get_session_direct
            with get_session_direct() as session:
                config = session.get(ReactorConfig, 1)
                if config is None:
                    config = ReactorConfig(id=1)
                    session.add(config)
                config.is_enabled = self.is_enabled
                config.symbol = self.enabled_symbol
                config.side = self.side
                config.amount = self.amount
                config.profit_pc = self.profit_pc
                from datetime import datetime as _dt
                config.updated_at = _dt.utcnow()
                session.commit()
                logger.debug(
                    f"[REACTOR] State persisted to DB — enabled={self.is_enabled}, "
                    f"symbol={self.enabled_symbol}"
                )
        except Exception as e:
            logger.error(f"[REACTOR] Failed to persist state to DB: {e}", exc_info=True)

    async def load_from_db(self) -> bool:
        """
        Restores reactor state from DB on backend startup.
        Returns True if a previously-enabled config was found and restored.
        """
        try:
            from app.db.database import ReactorConfig, get_session_direct
            with get_session_direct() as session:
                config = session.get(ReactorConfig, 1)
                if config is None:
                    logger.info("[REACTOR] No persisted config found — starting fresh.")
                    return False

                self.enabled_symbol = config.symbol
                self.side = config.side
                self.amount = config.amount
                self.profit_pc = config.profit_pc
                self.is_enabled = config.is_enabled

                if self.is_enabled:
                    logger.info(
                        f"[REACTOR] State restored from DB — symbol={config.symbol} | "
                        f"side={config.side} | amount={config.amount} | "
                        f"TP={config.profit_pc*100:.2f}%"
                    )
                    return True
                else:
                    logger.info("[REACTOR] Persisted config found but reactor was disabled. No auto-start.")
                    return False
        except Exception as e:
            logger.error(f"[REACTOR] Failed to load state from DB: {e}", exc_info=True)
            return False

    # ─────────────────────────────────────────────────────────────
    # Event hook — called by ChaseV2Service.handle_fill()
    # ─────────────────────────────────────────────────────────────

    async def on_position_closed(self, symbol: str, created_at: Optional[datetime] = None) -> None:
        """
        Async hook invoked when a Chase V2 cycle completes (TP placed successfully).

        V5.9.45 — Symbol Normalization:
        Uses exchange_manager.normalize_symbol to ensure consistent comparison
        (e.g. matching 1000PEPE/USDC:USDC from CCXT with 1000PEPE/USDC from config).

        Args:
            symbol:     CCXT-normalised symbol of the closed process.
            created_at: UTC datetime when the process was created (for cooldown calc).
        """
        if not self.is_enabled or not self.enabled_symbol:
            return

        # V5.9.48: Use Market ID for comparison to avoid CCXT formatting mismatches
        # (e.g. matching 1000PEPE/USDC:USDC with 1000PEPE/USDC)
        from app.core.exchange import exchange_manager
        id_closed = await exchange_manager.get_market_id(symbol)
        id_enabled = await exchange_manager.get_market_id(self.enabled_symbol)

        if id_closed != id_enabled:
            logger.debug(
                f"[REACTOR] Skipping — closed ID {id_closed} "
                f"does not match enabled ID {id_enabled}."
            )
            return

        # Ensure we use a normalized CCXT symbol for the follow-up chase
        norm_closed = await exchange_manager.normalize_symbol(symbol)

        # Cancel any previous pending task to avoid stacking
        if self._pending_task and not self._pending_task.done():
            self._pending_task.cancel()
            logger.warning("[REACTOR] Previous pending task cancelled (new cycle started).")

        self._pending_task = asyncio.create_task(
            self._delayed_chase(symbol=norm_closed, created_at=created_at)
        )

    # ─────────────────────────────────────────────────────────────
    # Internal logic
    # ─────────────────────────────────────────────────────────────

    def _calculate_cooldown(self, created_at: Optional[datetime]) -> float:
        """
        Calculates cooldown = 50% of the closed cycle duration.
        Uses created_at as cycle start and utcnow() as cycle end.
        Minimum floor: 30 seconds. Maximum cap: 3600 seconds (1 hour).

        V5.9.44: Accepts plain datetime primitive instead of ORM object.
        """
        now = datetime.utcnow()
        start = created_at or now
        duration_seconds = max((now - start).total_seconds(), 0.0)

        self.last_cycle_duration_seconds = duration_seconds
        cooldown = max(duration_seconds * 0.5, 30.0)  # floor: 30s
        cooldown = min(cooldown, 3600.0)               # cap: 1h

        logger.info(
            f"[REACTOR] Cycle duration: {duration_seconds:.1f}s → "
            f"Cooldown set to: {cooldown:.1f}s"
        )
        return cooldown

    async def _delayed_chase(self, symbol: str, created_at: Optional[datetime] = None) -> None:
        """
        Waits for the calculated cooldown, then fires a new Chase V2
        with the same parameters as the completed process.

        V5.9.44: Accepts plain primitives instead of ORM object.
        """
        try:
            cooldown = self._calculate_cooldown(created_at)
            self.last_cooldown_seconds = cooldown

            side = self.side          # Always use the value configured at enable-time
            amount = self.amount      # Always use the value configured at enable-time
            profit_pc = self.profit_pc

            logger.info(
                f"[REACTOR] Follow-up Chase scheduled in {cooldown:.1f}s — "
                f"{symbol} {side} {amount} @ {profit_pc*100:.2f}%"
            )

            await asyncio.sleep(cooldown)

            if not self.is_enabled:
                logger.info("[REACTOR] Reactor was disabled during wait. Aborting follow-up.")
                return

            # Lazy import to avoid circular dependency (per project DIP standard)
            from app.services.chase_v2_service import chase_v2_service

            logger.info(f"[REACTOR] Firing follow-up Chase for {symbol}...")
            result = await chase_v2_service.init_chase(
                symbol=symbol,
                side=side,
                amount=amount,
                profit_pc=profit_pc,
            )

            if result.get("success"):
                self.cycles_triggered += 1
                logger.info(
                    f"[REACTOR] ✅ Follow-up Chase #{self.cycles_triggered} launched successfully."
                )
            else:
                # V5.9.46 — Retry once after 30s before giving up.
                # Transient failures (price not available, -5022 exhausted) should not
                # silently kill the follow-up loop.
                err = result.get('error', 'Unknown error')
                logger.warning(
                    f"[REACTOR] ❌ Follow-up Chase failed: {err}. "
                    f"Retrying in 30s..."
                )
                await asyncio.sleep(30)
                if not self.is_enabled:
                    logger.info("[REACTOR] Reactor disabled during retry wait. Aborting.")
                    return
                retry_result = await chase_v2_service.init_chase(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    profit_pc=profit_pc,
                )
                if retry_result.get("success"):
                    self.cycles_triggered += 1
                    logger.info(
                        f"[REACTOR] ✅ Follow-up Chase #{self.cycles_triggered} launched on retry."
                    )
                else:
                    logger.error(
                        f"[REACTOR] ❌ Follow-up Chase failed after retry: "
                        f"{retry_result.get('error', 'Unknown error')}. "
                        f"Reactor remains enabled — waiting for next fill event."
                    )

        except asyncio.CancelledError:
            logger.info("[REACTOR] Delayed chase task was cancelled.")
        except Exception as e:
            logger.error(f"[REACTOR] Unexpected error in _delayed_chase: {e}", exc_info=True)


# Module-level singleton instance
close_fill_reactor = CloseFillReactor()
