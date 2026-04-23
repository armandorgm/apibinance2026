/**
 * API client for communicating with the Python backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface FillDetail {
  trade_id: string
  order_id: string
  price: number
  amount: number
  fee: number
  datetime: string
  role: string
}

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
  is_pending?: boolean
  order_type?: string | null
  tp_pnl?: number | null
  sl_pnl?: number | null
  /** Tipos de orden (Binance) calculados en backend */
  entry_order_tags?: string[]
  exit_order_tags?: string[]
  /** Binance Order IDs for reconciliation */
  entry_order_id?: string | null
  exit_order_id?: string | null
  /** Origin Centric fields */
  originator?: string
  can_be_entry?: boolean
  /** Salida vinculada (CONDITIONAL) calculada en el backend; mismo createTime que la entrada */
  conditional_exit?: {
    algo_id: string
    order_type: string
    side: string
    trigger_price: number
    create_time_ms: number
    conditional_kind?: string | null
    algo_type?: string | null
  } | null
  /** Nested Fills for UI Expansion */
  entry_fills?: FillDetail[]
  exit_fills?: FillDetail[]
}

export interface ExchangeLog {
  id: number
  method: string
  parameters: string | null
  response: string | null
  is_error: boolean
  error_message: string | null
  timestamp: number
  created_at: string
}

export interface Order {
  id: string
  symbol: string
  type: string
  side: string
  price: number
  amount: number
  filled: number
  remaining: number
  status: string
  datetime: string
  is_bot_logged: boolean
  is_algo: boolean
  error_message?: string
  /** LONG/SHORT/BOTH desde Binance openAlgoOrders */
  position_side?: string | null
  algo_type?: string | null
  /** take_profit | stop_loss | trailing */
  conditional_kind?: string | null
  closes_long?: boolean | null
  closes_short?: boolean | null
  /** Origin Centric Fields */
  originator: string
  source: string
  can_be_entry: boolean
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
  exchange_request: string | null
  exchange_response: string | null
  success: boolean
  error_message: string | null
  timestamp: number
  created_at: string
}

export interface ActivePipeline {
  id: number
  symbol: string
  pipeline_id: number
  entry_order_id: string | null
  last_tick_price: number | null
  last_order_price: number | null
  status: string
  sub_status: string
  retry_count: number
  side: string
  amount: number
  created_at: string | null
  finished_at: string | null
}

export interface ChaseSimulationRequest {
  current_price: number
  order_price: number
  last_tick_price?: number | null
  side: string
  last_update_iso: string
  cooldown_seconds?: number | null
  price_threshold?: number | null
  status: string
}

export interface ChaseSimulationResponse {
  status: string
  order_price: number
  should_update: boolean
  action?: string
  reason: string
  last_update_iso?: string
}

export interface BotConfig {
  id: number
  symbol: string
  interval: number
  is_enabled: boolean
  trade_amount: number
  updated_at: string
}

export interface WalletBalance {
  free: number
  used: number
  total: number
}

export interface AggregatedBalances {
  spot: Record<string, WalletBalance>
  futures: Record<string, WalletBalance>
  totals: Record<string, number>
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

export interface UcoeCandidate {
  id: string
  symbol: string
  type: string
  side: string
  price: number
  amount: number
  filled: number
  status: string
  timestamp: number
  datetime: string
  is_compatible_with_reduce_only: boolean
  is_orphan: boolean
}

export interface UcoePreview {
  symbol: string
  reference_order_id?: string
  reference_ids?: string[]
  reference_side: string
  reference_price?: number
  reference_price_avg?: number
  target_side: string
  target_price: number
  original_amount?: number
  original_total_amount?: number
  adjusted_amount?: number
  adjusted_total_amount?: number
  needs_scaling: boolean
  reduce_only: boolean
  profit_percentage: number
  position_context: {
    current_side: string
    net_pos: number
    timestamp?: number
    leverage?: number
  }
  projected_net_pos?: number
  missing_amount_to_zero?: number
  open_tp_qty?: number
  algo_units?: number
  basic_units?: number
  algo_breakdown?: {
    tp: number
    sl: number
    trailing: number
  }
  pos_units?: number
  action_units?: number
  algo_notional_est?: number
  basic_notional_est?: number
  action_notional_est?: number
}

export interface UcoeExecuteResponse {
  success: boolean
  order_id: string
  side: string
  price: string
  amount: string
  reduce_only: boolean
  is_bulk?: boolean
}

export async function fetchTrades(symbol: string, logic: string = 'fifo', sortBy: string = 'recent'): Promise<Trade[]> {
  const response = await fetch(`${API_BASE_URL}/api/trades/history?symbol=${encodeURIComponent(symbol)}&logic=${encodeURIComponent(logic)}&sort_by=${encodeURIComponent(sortBy)}`)
  
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

export async function fetchExchangeLogs(limit: number = 100, offset: number = 0): Promise<ExchangeLog[]> {
  const response = await fetch(`${API_BASE_URL}/api/exchange/logs?limit=${limit}&offset=${offset}`)
  if (!response.ok) throw new Error('Error fetching exchange logs')
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

export async function fetchBotConfig(): Promise<BotConfig> {
  const response = await fetch(`${API_BASE_URL}/api/bot/config`)
  if (!response.ok) throw new Error('Error fetching bot config')
  return response.json()
}

export async function updateBotConfig(config: Partial<BotConfig>): Promise<BotConfig> {
  const response = await fetch(`${API_BASE_URL}/api/bot/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!response.ok) throw new Error('Error updating bot config')
  return response.json()
}

export async function fetchBalances(): Promise<AggregatedBalances> {
  const response = await fetch(`${API_BASE_URL}/api/balances`)
  if (!response.ok) throw new Error('Error fetching balances')
  return response.json()
}

export async function fetchOpenOrders(symbol?: string): Promise<Order[]> {
  const url = new URL(`${API_BASE_URL}/api/orders/open`)
  if (symbol) url.searchParams.append('symbol', symbol)
  const response = await fetch(url.toString())
  if (!response.ok) throw new Error('Error fetching open orders')
  return response.json()
}

export async function fetchFailedOrders(limit: number = 50): Promise<BotSignal[]> {
  const response = await fetch(`${API_BASE_URL}/api/orders/failed?limit=${limit}`)
  if (!response.ok) throw new Error('Error fetching failed orders')
  return response.json()
}


// --- PIPELINES API ---

export interface PipelineMetadata {
  providers: string[]
  actions: string[]
  operators: string[]
}

export interface BotPipeline {
  id: number
  name: string
  symbol: string
  is_active: boolean
  trigger_event: string
  pipeline_config: string
  created_at: string
  updated_at: string
}

export async function fetchPipelineMetadata(): Promise<PipelineMetadata> {
  const response = await fetch(`${API_BASE_URL}/api/bot/pipelines/metadata`)
  if (!response.ok) throw new Error('Error fetching pipeline metadata')
  return response.json()
}

export async function fetchPipelines(): Promise<BotPipeline[]> {
  const response = await fetch(`${API_BASE_URL}/api/bot/pipelines`)
  if (!response.ok) throw new Error('Error fetching pipelines')
  return response.json()
}

export async function togglePipeline(id: number): Promise<BotPipeline> {
  const response = await fetch(`${API_BASE_URL}/api/bot/pipelines/${id}/toggle`, { method: 'PUT' })
  if (!response.ok) throw new Error('Error toggling pipeline')
  return response.json()
}

export async function deletePipeline(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/bot/pipelines/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Error deleting pipeline')
}

export async function createPipeline(payload: Partial<BotPipeline>): Promise<BotPipeline> {
  const response = await fetch(`${API_BASE_URL}/api/bot/pipelines`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error('Error creating pipeline')
  return response.json()
}

export async function triggerManualAction(
  symbol: string, 
  action_type: string,
  params?: {
    side?: string,
    amount?: number,
    threshold?: number,
    cooldown?: number,
    profit_pc?: number
  }
): Promise<{status: string, message: string}> {
  const response = await fetch(`${API_BASE_URL}/api/bot/manual-action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      symbol, 
      action_type,
      ...params
    }),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    const message = typeof err.detail === 'string' 
      ? err.detail 
      : JSON.stringify(err.detail || err) || 'Error triggering manual action';
    throw new Error(message);
  }
  return response.json()
}

export async function fetchActivePipelines(): Promise<ActivePipeline[]> {
  const response = await fetch(`${API_BASE_URL}/api/bot/active-pipelines`)
  if (!response.ok) throw new Error('Error fetching active pipelines')
  return response.json()
}

export async function stopPipeline(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/bot/active-pipelines/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Error stopping pipeline')
}

export async function simulateChase(req: ChaseSimulationRequest): Promise<ChaseSimulationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chase/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Error simulating chase: ${response.statusText}`)
  }
  return response.json()
}

// --- CHASE V2 API ---
export interface ChaseV2Status {
  id: number
  symbol: string
  side: string
  amount: number
  entry_order_id: string | null
  sub_status: string
  last_order_price: number | null
  last_tick_price: number | null
  created_at: string | null
  updated_at: string | null
}

export async function startChaseV2(symbol: string, side: string, amount: number, profitPc: number = 0.005): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/chase/init`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, side, amount, profit_pc: profitPc, pipeline_id: 0 }),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(err.detail || 'Error starting Chase V2')
  }
  return response.json()
}

export async function stopChaseV2(processId: number): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/chase/stop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ process_id: processId }),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(err.detail || 'Error stopping Chase V2')
  }
  return response.json()
}

export async function fetchChaseV2Status(symbol?: string): Promise<{ success: boolean, active_processes: ChaseV2Status[] }> {
  const url = new URL(`${API_BASE_URL}/api/chase/status`)
  if (symbol) url.searchParams.append('symbol', symbol)
  const response = await fetch(url.toString())
  if (!response.ok) throw new Error('Error fetching Chase V2 status')
  return response.json()
}


export async function fetchUcoeCandidates(symbol: string, filterMode: string = '7d', orphansOnly: boolean = false): Promise<UcoeCandidate[]> {
  const res = await fetch(`${API_BASE_URL}/api/unified-counter-order-engine/candidates?symbol=${encodeURIComponent(symbol)}&filter_mode=${filterMode}&orphans_only=${orphansOnly}`)
  if (!res.ok) throw new Error('Failed to fetch UCOE candidates')
  return res.json()
}

export async function fetchUcoePreview(symbol: string, orderId: string, profitPc: number = 0.5): Promise<UcoePreview> {
  const response = await fetch(`${API_BASE_URL}/api/unified-counter-order-engine/preview?symbol=${encodeURIComponent(symbol)}&order_id=${encodeURIComponent(orderId)}&profit_pc=${profitPc}`)
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error fetching UCOE preview')
  }
  return response.json()
}

export async function executeUcoeAction(symbol: string, orderId: string, profitPc: number = 0.5, overrideAmount?: number): Promise<UcoeExecuteResponse> {
  let url = `${API_BASE_URL}/api/unified-counter-order-engine/execute?symbol=${encodeURIComponent(symbol)}&order_id=${encodeURIComponent(orderId)}&profit_pc=${profitPc}`
  if (overrideAmount !== undefined) url += `&override_amount=${overrideAmount}`
  
  const response = await fetch(url, { method: 'POST' })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error executing UCOE action')
  }
  return response.json()
}

export async function fetchUcoeBulkPreview(symbol: string, orderIds: string[], profitPc: number = 0.5): Promise<UcoePreview> {
  const response = await fetch(`${API_BASE_URL}/api/unified-counter-order-engine/bulk-preview?symbol=${encodeURIComponent(symbol)}&order_ids=${orderIds.join(',')}&profit_pc=${profitPc}`)
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error fetching UCOE bulk preview')
  }
  return response.json()
}

export async function executeUcoeBulkAction(symbol: string, orderIds: string[], profitPc: number = 0.5, overrideAmount?: number): Promise<UcoeExecuteResponse> {
  let url = `${API_BASE_URL}/api/unified-counter-order-engine/bulk-execute?symbol=${encodeURIComponent(symbol)}&order_ids=${orderIds.join(',')}&profit_pc=${profitPc}`
  if (overrideAmount !== undefined) url += `&override_amount=${overrideAmount}`

  const response = await fetch(url, { method: 'POST' })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error executing UCOE bulk action')
  }
  return response.json()
}


export async function watchSymbol(symbol: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/watch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol }),
  })
  if (!response.ok) throw new Error('Error requesting symbol watch')
  return response.json()
}
