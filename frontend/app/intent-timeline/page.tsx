'use client'

import { useState } from 'react'
import { useTrades } from '@/hooks/use-trades'
import Link from 'next/link'
import { ArrowLeft, RefreshCw, Zap } from 'lucide-react'
import { IntentView } from '@/components/history/intent-view'

export default function IntentTimelinePage() {
  const [symbol, setSymbol] = useState('1000PEPEUSDC')
  
  // Usamos intent_fifo para garantizar pares 1:1 basados en intención (descartando SL)
  const { data: trades, isLoading, refetch, isFetching } = useTrades(symbol, 'intent_fifo', 'recent')

  return (
    <main className="min-h-screen bg-slate-950 flex flex-col overflow-hidden text-slate-100">
      {/* Cinematic Header */}
      <header className="flex-none p-6 bg-slate-900/40 backdrop-blur-xl border-b border-white/5 z-20">
        <div className="max-w-[1600px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link 
              href="/"
              className="group flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white rounded-xl transition-all border border-white/5"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              <span className="text-sm font-medium">Dashboard</span>
            </Link>
            
            <div className="flex flex-col">
              <div className="flex items-center gap-3">
                 <Zap className="w-5 h-5 text-amber-400 fill-amber-400" />
                 <h1 className="text-2xl font-black tracking-tighter uppercase italic">
                    Intent <span className="text-amber-500">Timeline</span>
                 </h1>
              </div>
              <p className="text-[10px] text-slate-500 uppercase tracking-[0.3em] font-bold mt-1 flex items-center gap-2">
                Order Intelligence Engine
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.8)]"></span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end mr-4 opacity-50">
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Logic Mode</span>
                <span className="text-xs font-mono text-amber-400">INTENT_FIFO_V2</span>
            </div>

            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="px-6 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-sm font-bold text-white focus:ring-2 focus:ring-amber-500 outline-none transition-all cursor-pointer hover:border-amber-500/50"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
              <option value="1000PEPEUSDC">1000PEPEUSDC</option>
            </select>
            
            <button
               onClick={() => refetch()}
               disabled={isFetching}
               className="p-3 bg-amber-500/10 text-amber-500 hover:bg-amber-500 hover:text-slate-950 rounded-xl transition-all disabled:opacity-50 border border-amber-500/20"
            >
              <RefreshCw className={`w-5 h-5 ${isFetching ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Viewport Area */}
      <div className="flex-1 relative bg-slate-950 w-full overflow-y-auto custom-scrollbar">
        {/* Ambient background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-64 bg-amber-500/5 blur-[120px] pointer-events-none rounded-full" />
        
        <div className="max-w-[1200px] mx-auto py-12 relative z-10">
            {isLoading ? (
            <div className="flex flex-col items-center justify-center py-32 space-y-6">
                <div className="relative">
                    <div className="w-16 h-16 border-2 border-amber-500/20 rounded-full animate-ping absolute inset-0"></div>
                    <div className="w-16 h-16 border-t-2 border-amber-500 rounded-full animate-spin"></div>
                </div>
                <div className="flex flex-col items-center">
                    <p className="text-sm font-black uppercase tracking-[0.4em] text-amber-500/80 animate-pulse">Syncing Intentions</p>
                    <p className="text-[10px] text-slate-600 mt-2">Mapeando órdenes atómicas 1:1...</p>
                </div>
            </div>
            ) : !trades || trades.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-32 text-slate-500 border border-dashed border-white/5 rounded-3xl mx-6">
                <Zap className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-lg font-medium">No active intentions found</p>
                <p className="text-sm opacity-60">Try synchronization in the main dashboard first.</p>
            </div>
            ) : (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <IntentView trades={trades} symbol={symbol} />
            </div>
            )}
        </div>
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      `}</style>
    </main>
  )
}
