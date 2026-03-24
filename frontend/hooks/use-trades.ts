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
      // Invalidate and refetch trades and stats after sync
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

      // Invalidate and refetch trades and stats after sync
      queryClient.invalidateQueries({ queryKey: ['trades', variables.symbol] })
      queryClient.invalidateQueries({ queryKey: ['stats', variables.symbol] })
    },
  })
}
