/**
 * React Query hooks for fetching trades data and bot status.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  fetchTrades, syncTrades, syncHistoricalTrades, fetchStats, 
  fetchBotStatus, fetchBotLogs, startBot, stopBot, fetchBotConfig, updateBotConfig, fetchBalances,
  fetchOpenOrders, fetchFailedOrders, fetchActivePipelines, stopPipeline,
  Trade, Stats, SyncResponse, BotStatus, BotSignal, BotConfig, AggregatedBalances, Order, ActivePipeline
} from '@/lib/api'

export function useTrades(symbol: string, logic: string = 'fifo', sortBy: string = 'recent') {
  return useQuery<Trade[]>({
    queryKey: ['trades', symbol, logic, sortBy],
    queryFn: () => fetchTrades(symbol, logic, sortBy),
    enabled: !!symbol,
  })
}

export function useStats(symbol: string, logic: string = 'fifo', includeUnrealized: boolean = false) {
  return useQuery<Stats>({
    queryKey: ['stats', symbol, logic, includeUnrealized],
    queryFn: () => fetchStats(symbol, logic, includeUnrealized),
    enabled: !!symbol,
  })
}

export function useSyncTrades() {
  const queryClient = useQueryClient()

  return useMutation<SyncResponse, Error, { symbol: string, logic: string }>({
    mutationFn: ({ symbol, logic }) => syncTrades(symbol, logic),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trades', variables.symbol] })
      queryClient.invalidateQueries({ queryKey: ['stats', variables.symbol] })
    },
  })
}

export function useSyncHistoricalTrades() {
  const queryClient = useQueryClient()

  return useMutation<SyncResponse, Error, { symbol: string; logic: string; endTime?: number }>({
    mutationFn: ({ symbol, logic, endTime }) => syncHistoricalTrades(symbol, logic, endTime),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trades', variables.symbol] })
      queryClient.invalidateQueries({ queryKey: ['stats', variables.symbol] })
    },
  })
}

export function useBotStatus() {
  return useQuery<BotStatus>({
    queryKey: ['bot-status'],
    queryFn: () => fetchBotStatus(),
    refetchInterval: 5000, // Refresh status every 5 seconds
  })
}

export function useBotLogs(limit: number = 10) {
  return useQuery<BotSignal[]>({
    queryKey: ['bot-logs', limit],
    queryFn: () => fetchBotLogs(limit),
    refetchInterval: 5000, // Refresh logs every 5 seconds
  })
}

export function useBotControl() {
    const queryClient = useQueryClient()
    
    const start = useMutation({
        mutationFn: startBot,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bot-status'] })
    })

    const stop = useMutation({
        mutationFn: stopBot,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bot-status'] })
    })

    return { start, stop }
}

export function useBotConfig() {
  return useQuery<BotConfig>({
    queryKey: ['bot-config'],
    queryFn: () => fetchBotConfig(),
  })
}

export function useUpdateBotConfig() {
  const queryClient = useQueryClient()

  return useMutation<BotConfig, Error, Partial<BotConfig>>({
    mutationFn: (config) => updateBotConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot-config'] })
      queryClient.invalidateQueries({ queryKey: ['bot-status'] })
    },
  })
}

export function useBalances() {
  return useQuery<AggregatedBalances>({
    queryKey: ['balances'],
    queryFn: () => fetchBalances(),
    refetchInterval: 60000, // Refresh every 1 minute
  })
}

export function useOpenOrders(symbol?: string) {
  return useQuery<Order[]>({
    queryKey: ['open-orders', symbol],
    queryFn: () => fetchOpenOrders(symbol),
    refetchInterval: 5000, // Refresh every 5 seconds
  })
}

export function useFailedOrders(limit: number = 50) {
  return useQuery<BotSignal[]>({
    queryKey: ['failed-orders', limit],
    queryFn: () => fetchFailedOrders(limit),
    refetchInterval: 10000,
  })
}

export function useActivePipelines() {
  return useQuery<ActivePipeline[]>({
    queryKey: ['active-pipelines'],
    queryFn: () => fetchActivePipelines(),
    refetchInterval: 2000, // Frequent refresh for live chase monitoring
  })
}

export function useStopPipeline() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => stopPipeline(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['active-pipelines'] })
    }
  })
}
