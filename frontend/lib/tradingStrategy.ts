/**
 * Configuration for the Functional Rules Motor.
 * This file defines the trading strategies as an array of evaluator functions.
 */

export interface TradingContext {
  last_purchase_time: number; // Unix timestamp in ms
  active_trades_count: number;
  last_range?: [number, number]; // e.g. [1, 4]
  current_time?: number;
}

export interface RuleActionResult {
  trigger: boolean;
  action?: 'NEW_ORDER' | 'UPDATE_RANGE';
  params?: Record<string, any>;
}

export type TradingRule = (context: TradingContext) => RuleActionResult;

/**
 * Rule 1 (Time): Trigger NEW_ORDER if last_purchase_age >= 24h.
 */
export const timeRule: TradingRule = (ctx) => {
  const currentTime = ctx.current_time || Date.now();
  const ageMs = currentTime - ctx.last_purchase_time;
  const isExpired = ageMs >= 24 * 60 * 60 * 1000;

  return {
    trigger: isExpired,
    action: isExpired ? 'NEW_ORDER' : undefined,
  };
};

/**
 * Rule 2 (Scaling Level 1): If active trades exist and last_range == [1, 4], set new_range = [25%, 75%].
 */
export const scalingL1Rule: TradingRule = (ctx) => {
  const hasActiveTrades = ctx.active_trades_count > 0;
  const isTargetRange = ctx.last_range && ctx.last_range[0] === 1 && ctx.last_range[1] === 4;

  if (hasActiveTrades && isTargetRange) {
    return {
      trigger: true,
      action: 'UPDATE_RANGE',
      params: { new_range: [25, 75] },
    };
  }

  return { trigger: false };
};

/**
 * Rule 3 (Scaling Level 2): If active trades persist, set new_range = [0%, 50%].
 */
export const scalingL2Rule: TradingRule = (ctx) => {
  const hasActiveTrades = ctx.active_trades_count > 0;

  // Since Rule 2 is level 1, Rule 3 is more aggressive.
  // Note: Priority is handled by RuleEngine order.
  if (hasActiveTrades) {
    return {
      trigger: true,
      action: 'UPDATE_RANGE',
      params: { new_range: [0, 50] },
    };
  }

  return { trigger: false };
};

/**
 * The Strategy Configuration: Array of evaluator functions.
 */
export const tradingStrategy: TradingRule[] = [
  timeRule,
  scalingL1Rule,
  scalingL2Rule,
];
