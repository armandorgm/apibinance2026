'use client'

import React, { useState } from 'react'
import { MethodSelector, MethodKey } from '@/components/history/method-selector'
import { PositionHistory } from '@/components/history/position-history'
import { useTrades, useSyncHistoricalTrades } from '@/hooks/use-trades'
import { TradeTable } from '@/components/trade-table' // Original view just for comparison if we wanted
import Link from 'next/link'

export default function HistoryPreviewPage() {
  const [symbol, setSymbol] = useState('1000PEPEUSDC')
  const [logic, setLogic] = useState<MethodKey>('atomic_fifo')
  const [sortBy, setSortBy] = useState('recent')

  const { data: trades, isLoading, refetch } = useTrades(symbol, logic, sortBy)

  return (
    <main className="min-h-screen p-8 bg-slate-50 dark:bg-slate-950">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-end justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3 text-slate-900 dark:text-white">
              <span className="p-2 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-lg">🎨</span>
              Preview: Rediseño Vistas de Historial
            </h1>
            <p className="text-slate-500 mt-2">
              Esta es una página temporal (sandboxed) para revisar las 4 nuevas representaciones visuales
              antes de integrarlas a la página principal.
            </p>
          </div>
          <Link href="/" className="px-4 py-2 border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 font-semibold shadow-sm transition-all">
            Volver al Dashboard
          </Link>
        </div>

        {/* CONTROLS */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm mb-6 flex flex-col gap-6">
          <div className="flex flex-wrap gap-6 items-end">
             {/* Symbol Select */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Símbolo</label>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="px-4 py-2.5 bg-slate-100 dark:bg-slate-800 border-none rounded-xl font-bold text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="BTC/USDT">BTC/USDT</option>
                <option value="ETH/USDT">ETH/USDT</option>
                <option value="1000PEPEUSDC">1000PEPEUSDC</option>
              </select>
            </div>

            {/* Sort Select */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Orden</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2.5 bg-slate-100 dark:bg-slate-800 border-none rounded-xl text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="recent">Recientes primero</option>
                <option value="oldest">Antiguos primero</option>
                <option value="pnl_desc">Mayor PnL primero</option>
              </select>
            </div>

            <button onClick={() => refetch()} className="ml-auto px-4 py-2.5 bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400 font-bold rounded-xl hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors">
              ↻ Actualizar Datos
            </button>
          </div>

          <hr className="border-slate-100 dark:border-slate-800" />
          
          {/* METHOD SELECTOR */}
          <div>
            <MethodSelector value={logic} onChange={setLogic} />
          </div>
        </div>

        {/* RESULTS WRAPPER */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-slate-200/60 dark:border-slate-800/60 overflow-hidden min-h-[500px]">
          <PositionHistory trades={trades || []} logic={logic} isLoading={isLoading} symbol={symbol} />
        </div>
      </div>
    </main>
  )
}
