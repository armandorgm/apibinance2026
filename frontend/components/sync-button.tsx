'use client'

import { useState } from 'react'
import { useSyncTrades } from '@/hooks/use-trades'
import { toast } from 'sonner'

interface SyncButtonProps {
  symbol: string
  logic: string
  onSyncComplete?: () => void
}

export function SyncButton({ symbol, logic, onSyncComplete }: SyncButtonProps) {
  const [isSyncing, setIsSyncing] = useState(false)
  const syncMutation = useSyncTrades()

  const handleSync = async () => {
    setIsSyncing(true)
    
    toast.promise(syncMutation.mutateAsync({ symbol, logic }), {
      loading: 'Sincronizando operaciones con Binance...',
      success: (result) => {
        onSyncComplete?.()
        return `Sincronización completada: ${result.message}`
      },
      error: (error) => `Error al sincronizar: ${error instanceof Error ? error.message : 'Error desconocido'}`,
      finally: () => setIsSyncing(false)
    })
  }

  return (
    <button
      onClick={handleSync}
      disabled={isSyncing}
      className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
    >
      {isSyncing ? (
        <>
          <svg
            className="animate-spin h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Sincronizando...
        </>
      ) : (
        <>
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Sincronizar con Binance
        </>
      )}
    </button>
  )
}
