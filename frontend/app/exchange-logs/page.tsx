'use client'

import { useEffect, useState } from 'react'
import { ExchangeLogsViewer } from '@/components/exchange-logs-viewer'
import { fetchExchangeLogs, ExchangeLog } from '@/lib/api'

export default function ExchangeLogsPage() {
  const [logs, setLogs] = useState<ExchangeLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadLogs = async () => {
    try {
      setLoading(true)
      const data = await fetchExchangeLogs(200, 0)
      setLogs(data)
      setError(null)
    } catch (err) {
      setError('Error al conectar con la API de logs del exchange')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadLogs()
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-center bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-indigo-600">
              CCXT Exchange Monitor
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Registro crudo de interacción hacia la API de Binance
            </p>
          </div>
          <button
            onClick={loadLogs}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loading ? 'Cargando...' : 'Actualizar'}
          </button>
        </div>

        {error ? (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded text-center">
            {error}
          </div>
        ) : (
          <ExchangeLogsViewer logs={logs} />
        )}
      </div>
    </div>
  )
}
