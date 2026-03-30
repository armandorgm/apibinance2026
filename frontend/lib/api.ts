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
  exit_side: string | null
  exit_price: number | null
  exit_amount: number | null
  exit_fee: number | null
  exit_datetime: string | null
  pnl_net: number
  pnl_percentage: number
  duration_seconds: number
  created_at: string
  is_orphan?: boolean
}

export interface Stats {
  total_trades: number
  total_pnl: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  average_pnl: number
  unrealized_pnl: number
}

export interface SyncResponse {
  success: boolean
  fills_added: number
  trades_created: number
  message: string
  start_time?: number
  end_time?: number
}

export interface BotSignal {
  id: number
  symbol: string
  rule_triggered: string | null
  action_taken: string | null
  params_snapshot: string | null
  success: boolean
  error_message: string | null
  timestamp: number
  created_at: string
}

export interface BotStatus {
  is_enabled: boolean
  last_run: {
    timestamp: string
    symbol: string
    rule_triggered: string | null
    action: string | null
    context: any
  } | null
}

export async function fetchTrades(symbol: string, logic: string = 'fifo'): Promise<Trade[]> {
  const response = await fetch(`${API_BASE_URL}/api/trades/history?symbol=${encodeURIComponent(symbol)}&logic=${encodeURIComponent(logic)}`)
  
  if (!response.ok) {
    throw new Error(`Error fetching trades: ${response.statusText}`)
  }
  
  return response.json()
}

export async function syncTrades(symbol: string, logic: string = 'atomic_fifo'): Promise<SyncResponse> {
  const response = await fetch(`${API_BASE_URL}/api/sync?symbol=${encodeURIComponent(symbol)}&logic=${encodeURIComponent(logic)}`, {
    method: 'POST',
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Error syncing trades: ${response.statusText}`)
  }
  
  return response.json()
}

export async function syncHistoricalTrades(symbol: string, logic: string = 'atomic_fifo', endTime?: number): Promise<SyncResponse> {
  const url = new URL(`${API_BASE_URL}/api/sync/historical`)
  url.searchParams.append('symbol', symbol)
  url.searchParams.append('logic', logic)
  if (endTime) {
    url.searchParams.append('end_time', endTime.toString())
  }

  const response = await fetch(url.toString(), {
    method: 'POST',
  })

  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Error syncing historical trades: ${response.statusText}`)
  }
  
  return response.json()
}

export async function fetchStats(symbol: string, logic: string = 'fifo', includeUnrealized: boolean = false): Promise<Stats> {
  const response = await fetch(`${API_BASE_URL}/api/stats?symbol=${encodeURIComponent(symbol)}&logic=${encodeURIComponent(logic)}&include_unrealized=${includeUnrealized}`)
  
  if (!response.ok) {
    throw new Error(`Error fetching stats: ${response.statusText}`)
  }
  
  return response.json()
}

export async function fetchBotStatus(): Promise<BotStatus> {
  const response = await fetch(`${API_BASE_URL}/api/bot/status`)
  if (!response.ok) throw new Error('Error fetching bot status')
  return response.json()
}

export async function fetchBotLogs(limit: number = 10): Promise<BotSignal[]> {
  const response = await fetch(`${API_BASE_URL}/api/bot/logs?limit=${limit}`)
  if (!response.ok) throw new Error('Error fetching bot logs')
  return response.json()
}

export async function startBot(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/bot/start`, { method: 'POST' })
    if (!response.ok) throw new Error('Error starting bot')
    return response.json()
}

export async function stopBot(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/bot/stop`, { method: 'POST' })
    if (!response.ok) throw new Error('Error stopping bot')
    return response.json()
}
