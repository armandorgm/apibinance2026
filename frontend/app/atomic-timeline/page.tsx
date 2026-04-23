'use client'

import { useState } from 'react'
import { useTrades } from '@/hooks/use-trades'
import Link from 'next/link'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import { GuitarHeroChart } from '@/components/guitar-hero-chart'

export default function AtomicTimelinePage() {
  const [symbol, setSymbol] = useState('1000PEPEUSDC')
  
  // Usamos atomic_fifo para garantizar pares 1:1
  const { data: trades, isLoading, refetch, isFetching } = useTrades(symbol, 'atomic_fifo', 'recent')

  return (
    <main className="min-h-screen bg-gray-950 flex flex-col overflow-hidden">
      {/* Immersive Header */}
      <header className="flex-none p-6 bg-gray-900/80 backdrop-blur-md border-b border-gray-800 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link 
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
            
            <div>
              <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                Neon Timeline
              </h1>
              <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold flex items-center gap-2">
                Atomic FIFO Engine 
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            >
             <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
              <option value="1000PEPEUSDC">1000PEPEUSDC</option>
            </select>
            
            <button
               onClick={() => refetch()}
               disabled={isFetching}
               className="p-2 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${isFetching ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Chart Area */}
      <div className="flex-1 relative bg-gray-950 w-full overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center text-gray-500 flex-col gap-4">
            <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
            <p className="animate-pulse tracking-widest uppercase text-sm font-semibold">Cargando flujos temporales...</p>
          </div>
        ) : !trades || trades.length === 0 ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            No se encontraron trades en formato Atomic FIFO para {symbol}.
          </div>
        ) : (
          <GuitarHeroChart trades={trades} />
        )}
      </div>
      
    </main>
  )
}
