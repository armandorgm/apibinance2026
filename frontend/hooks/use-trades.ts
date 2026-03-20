/**
 * React Query hooks for fetching trades data.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchTrades, syncTrades, syncHistoricalTrades, fetchStats, Trade, Stats, SyncResponse } from '@/lib/api'

export function useTrades(symbol: string, logic: string = 'fifo') {
  return useQuery<Trade[]>({
    queryKey: ['trades', symbol, logic],
    queryFn: () => fetchTrades(symbol, logic),
    enabled: !!symbol,
  })
}

export function useStats(symbol: string, logic: string = 'fifo') {
  return useQuery<Stats>({
    queryKey: ['stats', symbol, logic],
    queryFn: () => fetchStats(symbol, logic),
    enabled: !!symbol,
  })
}

export function useSyncTrades() {
  const queryClient = useQueryClient()

  return useMutation<SyncResponse, Error, { symbol: string }>({
    mutationFn: ({ symbol }) => syncTrades(symbol),
    onSuccess: (_, variables) => {
      // Invalidate and refetch trades and stats after sync
      queryClient.invalidateQueries({ queryKey: ['trades', variables.symbol] })
      queryClient.invalidateQueries({ queryKey: ['stats', variables.symbol] })
    },
  })
}

export function useSyncHistoricalTrades() {
  const queryClient = useQueryClient()

  return useMutation<SyncResponse, Error, { symbol: string }>({
    mutationFn: ({ symbol }) => syncHistoricalTrades(symbol),
    onSuccess: (_, variables) => {
      // Invalidate and refetch trades and stats after sync
      queryClient.invalidateQueries({ queryKey: ['trades', variables.symbol] })
      queryClient.invalidateQueries({ queryKey: ['stats', variables.symbol] })
    },
  })
}
