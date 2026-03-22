/**
 * Utility functions for formatting and calculations.
 */

/**
 * Formats a currency amount with an appropriate number of decimal places.
 * For low-priced tokens (e.g. < $1), it uses more decimals.
 * @param value The numerical value to format.
 * @param prefix An optional prefix (e.g. '$').
 * @returns A formatted string.
 */
export function formatPrice(value: number | null | undefined, prefix: string = '$'): string {
  if (value === null || value === undefined) return '—';
  
  // Choose precision based on value
  let decimals = 2;
  if (value < 0.1) decimals = 4;
  if (value < 0.01) decimals = 6;
  if (value < 0.0001) decimals = 8;
  
  return `${prefix}${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Formats a quantity with an appropriate number of decimal places.
 */
export function formatAmount(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  });
}

/**
 * Formats percentage.
 */
export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}%`;
}
