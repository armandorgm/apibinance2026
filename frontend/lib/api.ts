/**
 * API client for communicating with the Python backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Trade {
  id: number
  symbol: string
  entry_side: string
  entry_price: number
  entry_amount: number
  entry_fee: number
  entry_datetime: string
  exit_side: string
  exit_price: number
  exit_amount: number
  exit_fee: number
  exit_datetime: string
  pnl_net: number
  pnl_percentage: number
  duration_seconds: number
  created_at: string
}

export interface Stats {
  total_trades: number
  total_pnl: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  average_pnl: number
}

export interface SyncResponse {
  success: boolean
  fills_added: number
  trades_created: number
  message: string
}

export async function fetchTrades(symbol: string, logic: string = 'fifo'): Promise<Trade[]> {
  const response = await fetch(`${API_BASE_URL}/api/trades/history?symbol=${encodeURIComponent(symbol)}&logic=${encodeURIComponent(logic)}`)
  
  if (!response.ok) {
    throw new Error(`Error fetching trades: ${response.statusText}`)
  }
  
  return response.json()
}

export async function syncTrades(symbol: string): Promise<SyncResponse> {
  const response = await fetch(`${API_BASE_URL}/api/sync?symbol=${encodeURIComponent(symbol)}`, {
    method: 'POST',
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Error syncing trades: ${response.statusText}`)
  }
  
  return response.json()
}

export async function syncHistoricalTrades(symbol: string): Promise<SyncResponse> {
  const response = await fetch(`${API_BASE_URL}/api/sync/historical?symbol=${encodeURIComponent(symbol)}`, {
    method: 'POST',
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Error syncing historical trades: ${response.statusText}`)
  }
  
  return response.json()
}

export async function fetchStats(symbol: string, logic: string = 'fifo'): Promise<Stats> {
  const response = await fetch(`${API_BASE_URL}/api/stats?symbol=${encodeURIComponent(symbol)}&logic=${encodeURIComponent(logic)}`)
  
  if (!response.ok) {
    throw new Error(`Error fetching stats: ${response.statusText}`)
  }
  
  return response.json()
}
