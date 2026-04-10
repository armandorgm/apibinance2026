'use client'

import { useState } from 'react'
import { TradeTable } from '@/components/trade-table'
import { TradeChart } from '@/components/trade-chart'
import { SyncButton } from '@/components/sync-button'
import { StatsCard } from '@/components/stats-card'
import { BotMonitor } from '@/components/bot-monitor'
import { BalanceWidget } from '@/components/balance-widget'
import { OpenTradesTable } from '@/components/open-trades-table'
import { ManualActions } from '@/components/manual-actions'
import { useTrades, useStats, useSyncHistoricalTrades } from '@/hooks/use-trades'
import { formatPrice } from '@/lib/utils'
import Link from 'next/link'
import { Zap } from 'lucide-react'

export default function Home() {
  const [symbol, setSymbol] = useState('1000PEPEUSDC')
  const [logic, setLogic] = useState('atomic_fifo')
  const [sortBy, setSortBy] = useState('recent')
  const [includeUnrealized, setIncludeUnrealized] = useState(false)
  const [lastHistoricalEndTime, setLastHistoricalEndTime] = useState<number | undefined>(undefined)
  
  const { data: trades, isLoading, refetch } = useTrades(symbol, logic, sortBy)
  const { data: stats } = useStats(symbol, logic, includeUnrealized)
  const syncHistorical = useSyncHistoricalTrades()

  const handleSymbolChange = (newSymbol: string) => {
    setSymbol(newSymbol)
    setLastHistoricalEndTime(undefined)
  }

  const handleHistoricalSync = () => {
    syncHistorical.mutate({ symbol, logic, endTime: lastHistoricalEndTime }, {
      onSuccess: (data) => {
        if (data.start_time) {
          setLastHistoricalEndTime(data.start_time - 1)
        }
        alert(`Sincronización histórica:\n${data.message}`)
        refetch()
      },
      onError: (error) => {
        alert(`Error en carga histórica: ${error.message}`)
      }
    })
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Binance Futures Tracker
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Rastrea y analiza tus operaciones en Binance Futures
            </p>
          </div>
          <div className="flex gap-2">
            <a
              href="/pipelines"
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600/10 border border-indigo-200 hover:bg-indigo-600/20 text-indigo-700 dark:text-indigo-400 dark:border-indigo-800 rounded-xl font-bold transition-all shadow-sm active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              Pipelines
            </a>
            <Link
              href="/actions"
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700 rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 active:scale-95 px-6"
            >
              <Zap className="w-4 h-4 fill-white" />
              Acciones
            </Link>
            <a
              href="/orders"
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-300 rounded-xl font-bold transition-all shadow-sm active:scale-95"
            >
              📑 Monitor Órdenes
            </a>
            <Link href="/exchange-logs" className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-300 rounded-xl font-bold transition-all shadow-sm active:scale-95">
              📡 Logs Exchange
            </Link>
            <Link href="/api-tester" className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-emerald-900 border border-emerald-200 dark:border-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-800/80 text-emerald-700 dark:text-emerald-300 rounded-xl font-bold transition-all shadow-sm active:scale-95">
              🧪 API Tester
            </Link>
            <Link href="/chase-playground" className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-amber-900 border border-amber-200 dark:border-amber-700 hover:bg-amber-50 dark:hover:bg-amber-800/80 text-amber-700 dark:text-amber-300 rounded-xl font-bold transition-all shadow-sm active:scale-95">
              🧪 Chase Playground
            </Link>
            <a
              href="/settings"
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-300 rounded-xl font-bold transition-all shadow-sm active:scale-95"
            >
              ⚙️ Configurar Bot
            </a>
          </div>
        </div>

        {/* Controls */}
        <div className="mb-6 flex flex-wrap items-center gap-4">
          <div>
            <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Símbolo
            </label>
            <select
              id="symbol"
              value={symbol}
              onChange={(e) => handleSymbolChange(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
              <option value="1000PEPEUSDC">1000PEPEUSDC</option>
            </select>
          </div>
          <div>
            <label htmlFor="logic" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Método
            </label>
            <select
              id="logic"
              value={logic}
              onChange={(e) => setLogic(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="atomic_fifo">Atomic Match (FIFO)</option>
              <option value="atomic_lifo">Atomic Match (LIFO)</option>
              <option value="fifo">FIFO Puro (Parciales)</option>
              <option value="lifo">LIFO Puro (Parciales)</option>
            </select>
          </div>
          <div>
            <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Ordenar por
            </label>
            <select
              id="sortBy"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="recent">Más recientes primero</option>
              <option value="oldest">Más antiguas primero</option>
              <option value="pnl_desc">Mayor PnL primero</option>
            </select>
          </div>
          <div className="flex items-center gap-2 mt-6">
            <input
              type="checkbox"
              id="unrealized"
              checked={includeUnrealized}
              onChange={(e) => setIncludeUnrealized(e.target.checked)}
              className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <label htmlFor="unrealized" className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Incluir PnL Flotante (Abiertas)
            </label>
          </div>
          <div className="flex-1" />
          <button
            onClick={handleHistoricalSync}
            disabled={syncHistorical.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-lg font-medium transition-colors shadow-sm"
          >
            {syncHistorical.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Cargando...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {lastHistoricalEndTime ? 'Continuar previos (7 días)' : 'Cargar previos (7 días)'}
              </>
            )}
          </button>
          <SyncButton symbol={symbol} logic={logic} onSyncComplete={() => refetch()} />
        </div>


        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <StatsCard
              title="Total Trades"
              value={stats.total_trades.toString()}
              icon="📊"
            />
            <StatsCard
              title="PnL Neto"
              value={formatPrice(stats.total_pnl)}
              valueColor={stats.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}
              icon="💰"
            />
            <StatsCard
              title="Win Rate"
              value={`${stats.win_rate.toFixed(1)}%`}
              icon="🎯"
            />
            <StatsCard
              title="PnL Promedio"
              value={formatPrice(stats.average_pnl)}
              valueColor={stats.average_pnl >= 0 ? 'text-green-600' : 'text-red-600'}
              icon="📈"
            />
          </div>
        )}

        {/* Manual Actions - Removed as migrated to /actions */}
        {/* <div className="mb-8">
          <ManualActions symbol={symbol} />
        </div> */}

        {/* Bot Autonomous Monitoring and Balances */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
          <div className="xl:col-span-1">
            <BalanceWidget />
          </div>
          <div className="xl:col-span-2">
            <BotMonitor />
          </div>
        </div>

        {/* Chart */}
        {trades && trades.length > 0 && (
          <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Gráfico de Operaciones
            </h2>
            <TradeChart trades={trades} />
          </div>
        )}

        {/* Open Trades Section */}
        {trades && trades.length > 0 && (
          <OpenTradesTable trades={trades} />
        )}

        {/* Trade Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Historial de Posiciones
            </h2>
          </div>
          {isLoading ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              Cargando operaciones...
            </div>
          ) : (
            <TradeTable trades={trades || []} />
          )}
        </div>
      </div>
    </main>
  )
}
