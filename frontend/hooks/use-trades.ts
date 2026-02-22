/**
 * React Query hooks for fetching trades data.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchTrades, syncTrades, fetchStats, Trade, Stats, SyncResponse } from '@/lib/api'

export function useTrades(symbol: string) {
  return useQuery<Trade[]>({
    queryKey: ['trades', symbol],
    queryFn: () => fetchTrades(symbol),
    enabled: !!symbol,
  })
}

export function useStats(symbol: string) {
  return useQuery<Stats>({
    queryKey: ['stats', symbol],
    queryFn: () => fetchStats(symbol),
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
