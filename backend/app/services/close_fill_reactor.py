"""
CloseFillReactor — Bot B (Reactive Follow-Up System)

Designed by AI Agent — 2026-04-24
Responsibility: Single, isolated reactor that observes Chase V2 completions
and autonomously triggers follow-up chases with a dynamic cooldown.

SOLID compliance:
  - S: Dedicated only to reacting on fill events. No placement or tracking logic.
  - O: New behaviors (e.g. different cooldown strategies) extend, not modify.
  - D: Lazy imports break circular dependency with ChaseV2Service.

V5.9.44 — DetachedInstanceError fix:
  on_position_closed() now receives plain primitives (symbol, created_at)
  instead of the SQLAlchemy ORM object. This prevents SQLAlchemy from attempting
  an attribute refresh on a session-less (detached) instance when the async task
  fires after the DB session context has already closed.

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

    def disable(self) -> None:
        """Deactivates the reactor and cancels any pending follow-up task."""
        self.is_enabled = False
        if self._pending_task and not self._pending_task.done():
            self._pending_task.cancel()
            logger.info("[REACTOR] Pending follow-up task cancelled.")
        logger.info("[REACTOR] Disabled.")

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
    # Event hook — called by ChaseV2Service.handle_fill()
    # ─────────────────────────────────────────────────────────────

    async def on_position_closed(self, symbol: str, created_at: Optional[datetime] = None) -> None:
        """
        Async hook invoked when a Chase V2 cycle completes (TP placed successfully).

        V5.9.44: Accepts primitive values instead of the ORM object to prevent
        DetachedInstanceError when the async task fires after the DB session closes.

        Args:
            symbol:     CCXT-normalised symbol of the closed process.
            created_at: UTC datetime when the process was created (for cooldown calc).
        """
        if not self.is_enabled:
            return

        if symbol != self.enabled_symbol:
            logger.debug(
                f"[REACTOR] Skipping — closed symbol {symbol} "
                f"does not match enabled symbol {self.enabled_symbol}."
            )
            return

        # Cancel any previous pending task to avoid stacking
        if self._pending_task and not self._pending_task.done():
            self._pending_task.cancel()
            logger.warning("[REACTOR] Previous pending task cancelled (new cycle started).")

        self._pending_task = asyncio.create_task(
            self._delayed_chase(symbol=symbol, created_at=created_at)
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
                logger.error(
                    f"[REACTOR] ❌ Follow-up Chase failed: {result.get('error', 'Unknown error')}"
                )

        except asyncio.CancelledError:
            logger.info("[REACTOR] Delayed chase task was cancelled.")
        except Exception as e:
            logger.error(f"[REACTOR] Unexpected error in _delayed_chase: {e}", exc_info=True)


# Module-level singleton instance
close_fill_reactor = CloseFillReactor()
