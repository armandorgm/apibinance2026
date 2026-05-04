"""
ScheduledScalerBot — Bot C
==========================
Ejecuta órdenes de monto mínimo cada N horas (default: 8h) via Chase V2.

Diseño:
  - Singleton thread-safe, estado persistido en ScalerBotConfig (DB).
  - Side inferido dinámicamente en cada ciclo (posición actual + TP más cercano).
  - Si side de posición y side del TP son inconsistentes → abortar ciclo (no crash).
  - profit_pc = (P_actual + P_tp_cercano) / 2 fórmula midpoint, con floor=0.002.
  - Coexiste con CloseFillReactor (Bot B) sin interferencia.
  - Idempotencia: si ya hay un Chase CHASING del scaler activo → skip ciclo.

Implementado: 2026-04-25 | AI Agent — apibinance2026
"""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("apibinance2026")

# ──────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────
_PROFIT_FLOOR = 0.002          # min profit_pc (covers fees × 2 + slippage)
_BALANCE_SAFETY_MULTIPLIER = 1.1   # require 10% extra margin headroom


class ScheduledScalerBot:
    """
    Singleton that manages the periodic scaling execution loop.
    Persists state in the 'scaler_bot_config' DB table.
    """

    _instance: Optional["ScheduledScalerBot"] = None

    # ──────────────────────────────────────────────────────────────
    # Singleton factory
    # ──────────────────────────────────────────────────────────────
    def __new__(cls) -> "ScheduledScalerBot":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        # Live state (mirrors DB row while enabled)
        self.symbol: Optional[str] = None
        self.default_profit_pc: float = 0.005
        self.interval_hours: float = 8.0
        self.is_enabled: bool = False

        # Asyncio loop task
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    async def enable(
        self,
        symbol: str,
        default_profit_pc: float = 0.005,
        interval_hours: float = 8.0,
    ) -> dict:
        """
        Enables the scaler for a given symbol.
        Persists state to DB and launches the asyncio loop.
        """
        async with self._lock:
            self.symbol = symbol
            self.default_profit_pc = max(default_profit_pc, _PROFIT_FLOOR)
            self.interval_hours = interval_hours
            self.is_enabled = True

            await self._persist_config(is_enabled=True)

            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._run_loop())
                logger.info(
                    f"[SCALER] Enabled for {symbol} | interval={interval_hours}h "
                    f"| default_profit_pc={self.default_profit_pc}"
                )

        return self.get_status()

    async def disable(self) -> dict:
        """
        Disables the scaler. The running loop detects the flag and exits cleanly.
        """
        async with self._lock:
            self.is_enabled = False
            await self._persist_config(is_enabled=False)
            logger.info("[SCALER] Disabled by user request.")
        return self.get_status()

    def get_status(self) -> dict:
        return {
            "is_enabled": self.is_enabled,
            "symbol": self.symbol,
            "default_profit_pc": self.default_profit_pc,
            "interval_hours": self.interval_hours,
            "loop_running": self._task is not None and not self._task.done(),
        }

    # ──────────────────────────────────────────────────────────────
    # Persistence
    # ──────────────────────────────────────────────────────────────

    async def _persist_config(self, is_enabled: bool, **kwargs) -> None:
        """Upserts the ScalerBotConfig row for self.symbol."""
        from app.db.database import ScalerBotConfig, get_session_direct
        from sqlmodel import select

        def _write():
            with get_session_direct() as session:
                stmt = select(ScalerBotConfig).where(
                    ScalerBotConfig.symbol == self.symbol
                )
                row = session.exec(stmt).first()
                if row is None:
                    row = ScalerBotConfig(symbol=self.symbol)
                    session.add(row)

                row.is_enabled = is_enabled
                row.default_profit_pc = self.default_profit_pc
                row.interval_hours = self.interval_hours
                row.updated_at = datetime.utcnow()

                for key, val in kwargs.items():
                    setattr(row, key, val)

                session.commit()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _write)

    async def load_from_db(self) -> bool:
        """
        Called at backend startup: restores enabled state if the DB row is marked enabled.
        Returns True if the bot was re-enabled.
        """
        from app.db.database import ScalerBotConfig, get_session_direct
        from sqlmodel import select

        def _read():
            with get_session_direct() as session:
                return session.exec(
                    select(ScalerBotConfig).where(ScalerBotConfig.is_enabled == True)
                ).first()

        loop = asyncio.get_event_loop()
        row: Optional[ScalerBotConfig] = await loop.run_in_executor(None, _read)

        if row:
            logger.info(f"[SCALER] Restoring persistent state for {row.symbol}")
            await self.enable(
                symbol=row.symbol,
                default_profit_pc=row.default_profit_pc,
                interval_hours=row.interval_hours,
            )
            return True
        return False

    # ──────────────────────────────────────────────────────────────
    # Main loop
    # ──────────────────────────────────────────────────────────────

    async def _run_loop(self) -> None:
        """
        8-hour (or configured) loop. Checks for shutdown every 60 seconds
        to allow clean exit without blocking the full sleep duration.
        """
        logger.info(
            f"[SCALER] Loop started — executing every {self.interval_hours}h for {self.symbol}"
        )

        # First cycle immediately on enable
        await self._execute_cycle()

        while self.is_enabled:
            # Sleep in 60s chunks so disable() takes effect quickly
            interval_seconds = int(self.interval_hours * 3600)
            elapsed = 0
            while elapsed < interval_seconds and self.is_enabled:
                await asyncio.sleep(60)
                elapsed += 60

            if not self.is_enabled:
                break

            await self._execute_cycle()

        logger.info("[SCALER] Loop exited cleanly.")

    # ──────────────────────────────────────────────────────────────
    # Cycle logic
    # ──────────────────────────────────────────────────────────────

    async def _execute_cycle(self) -> None:
        """
        One full scaler cycle:
          0. Persistence Guard: skip if enough time hasn't passed (prevents multi-run on restarts).
          1. Infer side from position + nearest TP (must agree).
          2. Verify balance ≥ min_notional × safety_multiplier.
          3. Compute profit_pc via midpoint formula.
          4. Guard: skip if a scaler Chase is already CHASING.
          5. Invoke ChaseV2Service.init_chase.
        """
        symbol = self.symbol
        logger.info(f"[SCALER] Cycle start for {symbol}")

        try:
            from app.db.database import ScalerBotConfig, get_session_direct
            from sqlmodel import select
            
            # ── Step 0: Persistence Guard ─────────────────────────
            def _get_config():
                with get_session_direct() as session:
                    return session.exec(
                        select(ScalerBotConfig).where(ScalerBotConfig.symbol == symbol)
                    ).first()
            
            loop = asyncio.get_event_loop()
            config: Optional[ScalerBotConfig] = await loop.run_in_executor(None, _get_config)
            
            if config and config.last_execution_at:
                now = datetime.utcnow()
                diff = now - config.last_execution_at
                required_diff = timedelta(hours=config.interval_hours)
                
                if diff < required_diff:
                    remaining = required_diff - diff
                    logger.info(
                        f"[SCALER] Skipping cycle for {symbol}: only {diff.total_seconds()/60:.1f}m elapsed "
                        f"since last execution at {config.last_execution_at}. "
                        f"Next run in {remaining.total_seconds()/60:.1f}m."
                    )
                    return

            from app.core.binance_native import binance_native
            from app.core.exchange import exchange_manager

            # ── Step 1: Infer side ────────────────────────────────
            side, current_price, nearest_tp_price, leverage = await self._infer_side_and_tp(
                symbol, binance_native
            )
            if side is None:
                # Only genuine failures reach here: TP side mismatch
                logger.warning(
                    f"[SCALER] Side inference failed for {symbol}, skipping cycle. "
                    f"Reason: TP side mismatch — check logs above for detail."
                )
                await self._log_signal(
                    symbol, "INFER", "HOLD", success=False,
                    error="Side inference failed (TP side mismatch)"
                )
                return

            # ── Step 1b: Price guard ──────────────────────────────
            # Flat-fallback may return price=0.0 if ticker failed during _infer_side_and_tp.
            # fetch_ticker() is the async CCXT method; get_ticker() is sync in-memory cache only.
            if current_price <= 0:
                try:
                    ticker = await exchange_manager.fetch_ticker(symbol)
                    current_price = float(ticker.get("last") or ticker.get("close") or 0.0)
                    logger.info(f"[SCALER] Price recovered from ticker: {current_price}")
                except Exception as e:
                    logger.warning(f"[SCALER] Ticker fetch failed: {e}")
                if current_price <= 0:
                    logger.warning(
                        f"[SCALER] Cannot determine price for {symbol} (price=0). Skipping cycle."
                    )
                    return

            # ── Step 2: Balance check ─────────────────────────────
            quote_asset = _extract_quote_asset(symbol)
            available = await binance_native.get_available_balance(quote_asset)
            min_qty = await exchange_manager.get_safe_min_notional_qty(symbol, current_price)
            
            notional_required = min_qty * current_price * _BALANCE_SAFETY_MULTIPLIER
            min_cost = notional_required / leverage
            
            logger.info(
                f"[SCALER] Balance Check | available={available:.4f} {quote_asset} | "
                f"required_margin={min_cost:.4f} (notional={notional_required:.4f}, leverage={leverage}x)"
            )

            if available < min_cost:
                msg = f"Insufficient balance: {available:.4f} < {min_cost:.4f} required."
                logger.warning(f"[SCALER] {msg} Skipping cycle.")
                await self._log_signal(
                    symbol, "BALANCE", "HOLD", success=False, error=msg
                )
                return

            # ── Step 3: Compute profit_pc ─────────────────────────
            profit_pc = self._compute_profit_pc(
                current_price=current_price,
                nearest_tp_price=nearest_tp_price,
                side=side,
            )
            logger.info(
                f"[SCALER] Computed profit_pc={profit_pc:.4f} "
                f"(current={current_price}, tp={nearest_tp_price})"
            )

            # ── Step 4: Idempotency guard ─────────────────────────
            if self._has_active_scaler_chase(symbol, side):
                logger.info(
                    f"[SCALER] Active scaler Chase detected for {symbol}/{side}, "
                    "skipping cycle."
                )
                await self._log_signal(
                    symbol, "IDEMPOTENCY", "HOLD", error="Active scaler Chase already running"
                )
                return

            # ── Step 5: Launch Chase V2 ───────────────────────────
            from app.services.chase_v2_service import ChaseV2Service

            chase = ChaseV2Service()
            amount_usd = min_qty * current_price
            logger.info(
                f"[SCALER] Launching Chase V2 | sym={symbol} side={side} "
                f"amount_usd={amount_usd:.4f} (qty={min_qty}) profit_pc={profit_pc}"
            )
            result = await chase.init_chase(
                symbol=symbol,
                side=side,
                amount=amount_usd,
                profit_pc=profit_pc,
                originator="SCALER_BOT",
            )
            logger.info(f"[SCALER] Chase launched: {result}")

            import json
            await self._log_signal(
                symbol, "EXEC", "NEW_ORDER", 
                resp=json.dumps(result) if isinstance(result, dict) else str(result)
            )

            # ── Persist cycle stats ───────────────────────────────
            await self._persist_config(
                is_enabled=True,
                cycles_executed=await self._increment_cycles(),
                last_execution_at=datetime.utcnow(),
                last_cycle_side=side,
                last_profit_pc_used=profit_pc,
            )

        except Exception as exc:
            logger.error(f"[SCALER] Cycle error: {exc}", exc_info=True)
            await self._log_signal(
                symbol, "CRITICAL", "ERROR", success=False, error=str(exc)
            )

    # ──────────────────────────────────────────────────────────────
    # Side inference
    # ──────────────────────────────────────────────────────────────

    async def _infer_side_and_tp(
        self, symbol: str, engine
    ) -> tuple[Optional[str], float, Optional[float], float]:
        """
        Returns (side, current_price, nearest_tp_price).
        Returns (None, 0.0, None) on abort.

        Logic:
          - Get positionRisk → derive position_side from positionAmt sign.
          - Get open orders → filter reduceOnly=True LIMIT orders.
          - For LONG (buy): nearest TP = lowest SELL order above current_price.
          - For SHORT (sell): nearest TP = highest BUY order below current_price.
          - If TP's implied side matches position_side → proceed.
          - If they disagree → abort.
        """
        from app.core.exchange import exchange_manager
        
        # Try CCXT first via ExchangeManager
        try:
            ccxt_symbol = await exchange_manager.normalize_symbol(symbol)
            native_symbol = await exchange_manager.get_market_id(ccxt_symbol)
            
            logger.info(f"[SCALER] Symbol check: input={symbol}, ccxt={ccxt_symbol}, native={native_symbol}")
            
            positions = await exchange_manager.get_open_positions(ccxt_symbol)
        except Exception as e:
            logger.error(f"[SCALER] Error in exchange_manager: {e}")
            positions = []
            native_symbol = await exchange_manager.get_market_id(symbol)

        target_pos = None
        if positions:
            target_pos = positions[0]
            position_amt = float(target_pos.get("contracts") or 0.0)
            current_price = float(target_pos.get("last") or target_pos.get("markPrice") or 0.0)
            
            # Robust leverage extraction for CCXT source
            leverage = float(target_pos.get("leverage") or 0.0)
            if leverage <= 1.0:
                # Check info sub-object for native Binance fields
                info = target_pos.get("info", {})
                leverage = float(info.get("leverage") or 0.0)
                
                if leverage <= 1.0:
                    # Fallback to math
                    notional = abs(float(target_pos.get("notional") or info.get("notional") or 0.0))
                    initial_margin = float(target_pos.get("initialMargin") or info.get("initialMargin") or 0.0)
                    if initial_margin > 0:
                        leverage = round(notional / initial_margin)
                    else:
                        leverage = 1.0
            
            logger.info(f"[SCALER] Leverage from controlador (CCXT) for {ccxt_symbol}: {leverage}x")
        else:
            # Fallback to native engine
            native_positions = await engine.get_position_risk(native_symbol)
            
            for p in native_positions:
                if p.get("symbol") == native_symbol:
                    target_pos = p
                    break
            
            if not target_pos:
                # No position record at all → treat as flat → LONG fallback
                logger.info(
                    f"[SCALER] No position record found via CCXT or Native for {symbol} (Native: {native_symbol}). "
                    f"Assuming FLAT state. Triggering Recovery Fallback to LONG (side=buy)."
                )
                current_price_fb = 0.0
                try:
                    ticker = await exchange_manager.get_ticker(symbol)
                    current_price_fb = float(ticker.get("last") or ticker.get("close") or 0.0)
                    logger.info(f"[SCALER] Recovery ticker price for {symbol}: {current_price_fb}")
                except Exception as e:
                    logger.warning(f"[SCALER] Recovery ticker fetch failed: {e}")
                return "buy", current_price_fb, None, 1.0

            position_amt = float(target_pos.get("positionAmt") or 0.0)
            current_price = float(target_pos.get("markPrice") or 0.0)

            # Robust leverage extraction for Native source
            leverage = float(target_pos.get("leverage") or 0.0)
            if leverage <= 1.0:
                notional = abs(float(target_pos.get("notional") or 0.0))
                initial_margin = float(target_pos.get("initialMargin") or 0.0)
                if initial_margin > 0:
                    leverage = round(notional / initial_margin)
                else:
                    leverage = 1.0
            logger.info(f"[SCALER] Leverage from native engine for {native_symbol}: {leverage}x")

        if position_amt == 0.0:
            # positionAmt is exactly 0 → flat → LONG fallback
            logger.info(
                f"[SCALER] Position for {symbol} is FLAT (positionAmt=0). "
                f"Executing default cycle fallback to LONG (side=buy). Leverage={leverage}x."
            )
            return "buy", current_price, None, leverage

        position_side = "buy" if position_amt > 0 else "sell"

        # Fetch open orders and find nearest TP
        open_orders = await engine.get_open_orders(native_symbol)
        reduce_only_limits = [
            o for o in open_orders
            if o.get("reduceOnly") and o.get("type") == "LIMIT"
        ]
        logger.info(
            f"[SCALER] Syncing TPs for {native_symbol}: found {len(reduce_only_limits)} "
            f"reduceOnly LIMIT orders out of {len(open_orders)} total open orders."
        )

        nearest_tp_price: Optional[float] = None
        tp_implied_side: Optional[str] = None

        if position_side == "buy":
            # TPs for LONG are SELL orders above current price
            candidates = [
                o for o in reduce_only_limits
                if o.get("side", "").upper() == "SELL"
                and float(o.get("price", 0)) > current_price
            ]
            if candidates:
                best = min(candidates, key=lambda o: float(o["price"]))
                nearest_tp_price = float(best["price"])
                tp_implied_side = "buy"  # TP is closing a LONG → underlying side = buy

        else:  # position_side == "sell"
            # TPs for SHORT are BUY orders below current price
            candidates = [
                o for o in reduce_only_limits
                if o.get("side", "").upper() == "BUY"
                and float(o.get("price", 0)) < current_price
            ]
            if candidates:
                best = max(candidates, key=lambda o: float(o["price"]))
                nearest_tp_price = float(best["price"])
                tp_implied_side = "sell"  # TP is closing a SHORT → underlying side = sell

        # Agreement check
        if nearest_tp_price is None:
            logger.info(
                f"[SCALER] No existing TP orders detected for {native_symbol}/{position_side}. "
                f"Defaulting to configured profit_pc={self.default_profit_pc}"
            )
            # No TP found → use default, but side is inferred from position
            return position_side, current_price, None, leverage

        if tp_implied_side != position_side:
            logger.warning(
                f"[SCALER] Side mismatch: position_side={position_side} "
                f"vs tp_implied_side={tp_implied_side}. Aborting cycle."
            )
            return None, current_price, None, leverage

        logger.info(
            f"[SCALER] Inferred side={position_side}, current={current_price}, "
            f"nearest_tp={nearest_tp_price}, leverage={leverage}x"
        )
        return position_side, current_price, nearest_tp_price, leverage

    # ──────────────────────────────────────────────────────────────
    # Profit computation
    # ──────────────────────────────────────────────────────────────

    def _compute_profit_pc(
        self,
        current_price: float,
        nearest_tp_price: Optional[float],
        side: str,
    ) -> float:
        """
        Midpoint formula:
          target = (P_current + P_nearest_TP) / 2
          profit_pc = |target - P_current| / P_current
                    = |P_nearest_TP - P_current| / (2 * P_current)
        Floor: max(profit_pc, 0.002) to cover fees.
        If no TP found → return default_profit_pc.
        """
        if nearest_tp_price is None or current_price <= 0:
            return self.default_profit_pc

        gap = abs(nearest_tp_price - current_price)
        profit_pc = gap / (2.0 * current_price)

        return max(profit_pc, _PROFIT_FLOOR)

    # ──────────────────────────────────────────────────────────────
    # Idempotency guard
    # ──────────────────────────────────────────────────────────────

    def _has_active_scaler_chase(self, symbol: str, side: str) -> bool:
        """
        Checks DB for any CHASING BotPipelineProcess launched by SCALER_BOT
        for the same symbol + side.
        """
        from app.db.database import BotPipelineProcess, get_session_direct
        from sqlmodel import select

        with get_session_direct() as session:
            stmt = (
                select(BotPipelineProcess)
                .where(BotPipelineProcess.symbol == symbol)
                .where(BotPipelineProcess.side == side)
                .where(BotPipelineProcess.status == "CHASING")
                # handler_type is always CHASE_V2 but originator distinguishes
            )
            result = session.exec(stmt).first()
            return result is not None

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    async def _increment_cycles(self) -> int:
        """Read current cycle count from DB and return incremented value."""
        from app.db.database import ScalerBotConfig, get_session_direct
        from sqlmodel import select

        def _read():
            with get_session_direct() as session:
                row = session.exec(
                    select(ScalerBotConfig).where(
                        ScalerBotConfig.symbol == self.symbol
                    )
                ).first()
                return row.cycles_executed if row else 0

        loop = asyncio.get_event_loop()
        current = await loop.run_in_executor(None, _read)
        return current + 1

    async def _log_signal(
        self, 
        symbol: str, 
        rule: str, 
        action: str, 
        success: bool = True, 
        error: Optional[str] = None, 
        resp: Optional[str] = None
    ) -> None:
        """Saves a record to the bot_signals table for UI tracking."""
        from app.db.database import BotSignal, get_session_direct

        def _write():
            with get_session_direct() as session:
                sig = BotSignal(
                    symbol=symbol,
                    rule_triggered=f"SCALER_{rule}",
                    action_taken=action,
                    success=success,
                    error_message=error,
                    exchange_response=resp
                )
                session.add(sig)
                session.commit()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _write)


# ──────────────────────────────────────────────────────────────────
# Module-level helpers
# ──────────────────────────────────────────────────────────────────

def _extract_quote_asset(symbol: str) -> str:
    """
    Derives the quote currency from a Binance Futures symbol string.
    Examples:
      '1000PEPE/USDC:USDC' → 'USDC'
      'BTC/USDT:USDT'      → 'USDT'
      '1000PEPEUSDC'       → 'USDC'   (native format)
      'BTCUSDT'            → 'USDT'   (native format, fallback)
    """
    # CCXT format: 'BASE/QUOTE:SETTLE'
    if "/" in symbol:
        parts = symbol.split("/")
        quote_part = parts[1].split(":")[0]
        return quote_part

    # Native format: strip known bases with regex
    # Match trailing known quote currencies
    match = re.search(r"(USDT|USDC|BUSD|USD|BTC|ETH|BNB)$", symbol)
    if match:
        return match.group(1)

    # Ultimate fallback
    logger.warning(f"[SCALER] Could not extract quote asset from symbol '{symbol}', defaulting to USDC")
    return "USDC"


# Module-level singleton
scheduled_scaler_bot = ScheduledScalerBot()
