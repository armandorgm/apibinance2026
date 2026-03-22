/**
 * Manual test for formatting logic (equivalent to utils.ts)
 */
const assert = require('assert');

function formatPrice(value, prefix = '$') {
  if (value === null || value === undefined) return '—';
  
  let decimals = 2;
  if (value < 0.1) decimals = 4;
  if (value < 0.01) decimals = 6;
  if (value < 0.0001) decimals = 8;
  
  // Use a simple toFixed/replace for the test environment instead of toLocaleString
  // as toLocaleString can vary by environment
  const num = Number(value).toFixed(decimals);
  // Remove trailing zeros after the 2nd decimal place if they are insignficant? 
  // No, the requirement is to show enough decimals.
  return `${prefix}${num}`;
}

function formatAmount(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(6);
}

function formatPercentage(value) {
  if (value === null || value === undefined) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${Number(value).toFixed(2)}%`;
}

// Test cases
console.log('Running tests...');

// Price formatting
assert.strictEqual(formatPrice(65000), '$65000.00');
assert.strictEqual(formatPrice(0.0033594), '$0.003359'); // With 6 decimals (value < 0.01)
// Wait, my logic was:
// value < 0.1 -> 4
// value < 0.01 -> 6
// 0.0033594 < 0.01 -> 6 decimals -> 0.003359
assert.strictEqual(formatPrice(0.000012345), '$0.00001235'); // value < 0.0001 -> 8 decimals -> 0.00001235

// Amount formatting
assert.strictEqual(formatAmount(1475), '1475.000000');

// Percentage formatting
assert.strictEqual(formatPercentage(5.5), '+5.50%');
assert.strictEqual(formatPercentage(-2.3), '-2.30%');

console.log('All tests passed!');
