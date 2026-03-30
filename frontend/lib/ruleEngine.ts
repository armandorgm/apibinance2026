/**
 * Functional Rules Motor (Evaluator).
 * Processes a trading context against a set of rules.
 */
import { TradingContext, TradingRule, RuleActionResult } from './tradingStrategy';

export class RuleEngine {
  private rules: TradingRule[];

  constructor(rules: TradingRule[]) {
    this.rules = rules;
  }

  /**
   * Evaluates the context and returns the FIRST rule that triggers.
   * Priority is determined by the order in the array.
   */
  evaluate(context: TradingContext): RuleActionResult {
    for (const rule of this.rules) {
      const result = rule(context);
      if (result.trigger) {
        return result;
      }
    }

    return { trigger: false };
  }

  /**
   * Evaluates all rules and returns all results that triggered.
   */
  evaluateAll(context: TradingContext): RuleActionResult[] {
    return this.rules
      .map(rule => rule(context))
      .filter(result => result.trigger);
  }
}
