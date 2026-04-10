'use client'

import { useState } from 'react'
import { triggerManualAction } from '@/lib/api'
import { Zap, ShoppingCart, Loader2, DollarSign, Settings2, ShieldAlert } from 'lucide-react'

interface ActionFormProps {
  symbol: string
}

export function ChaseEntryForm({ symbol }: ActionFormProps) {
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [amount, setAmount] = useState('20')
  const [isLoading, setIsLoading] = useState(false)
  const [useCustomThreshold, setUseCustomThreshold] = useState(false)
  const [threshold, setThreshold] = useState(0.0005)

  const handleAction = async () => {
    try {
      setIsLoading(true)
      await triggerManualAction(symbol, 'ADAPTIVE_OTO')
      alert(`Éxito: Chase iniciado en ${symbol}`)
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-[2.5rem] p-8 shadow-xl border border-gray-100 dark:border-gray-800 overflow-hidden relative">
       <div className="absolute top-0 right-0 p-8 opacity-5">
        <Zap className="w-32 h-32 fill-current" />
      </div>
      
      <div className="flex items-center gap-4 mb-10">
        <div className="p-4 bg-amber-100 dark:bg-amber-900/30 rounded-2xl text-amber-600 dark:text-amber-400">
          <Zap className="w-8 h-8 fill-current" />
        </div>
        <div>
          <h2 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">Chase Entry</h2>
          <p className="text-gray-500 dark:text-gray-400">Estrategia adaptativa Post-Only con OTO (Take Profit) integrado.</p>
        </div>
      </div>

      <div className="space-y-8">
        <div className="grid grid-cols-2 gap-4 p-1.5 bg-gray-50 dark:bg-gray-950 rounded-[1.5rem] border border-gray-100 dark:border-gray-800">
          <button
            onClick={() => setSide('buy')}
            className={`py-4 rounded-2xl font-black text-sm transition-all ${side === 'buy' ? 'bg-green-600 text-white shadow-xl scale-[1.02]' : 'text-gray-400 hover:text-gray-600'}`}
          >
            LONG POSITON
          </button>
          <button
            onClick={() => setSide('sell')}
            className={`py-4 rounded-2xl font-black text-sm transition-all ${side === 'sell' ? 'bg-red-600 text-white shadow-xl scale-[1.02]' : 'text-gray-400 hover:text-gray-600'}`}
          >
            SHORT POSITION
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-2">
            <label className="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Monto de Entrada (USD)</label>
            <div className="relative">
              <DollarSign className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full pl-12 pr-6 py-5 bg-gray-50 dark:bg-gray-950 border border-gray-100 dark:border-gray-800 rounded-3xl focus:ring-4 focus:ring-amber-500/10 focus:border-amber-500 transition-all outline-none text-xl font-bold"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-black uppercase tracking-widest text-gray-400 ml-1 flex justify-between">
              Umbral de Chase %
              <span className="text-amber-500">{(threshold * 100).toFixed(3)}%</span>
            </label>
            <div className="px-6 py-5 bg-gray-50 dark:bg-gray-950 border border-gray-100 dark:border-gray-800 rounded-3xl">
              <input
                type="range"
                min="0.0001"
                max="0.0050"
                step="0.0001"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full accent-amber-500"
              />
            </div>
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-amber-50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-900/20 flex gap-4">
            <ShieldAlert className="w-6 h-6 text-amber-600 shrink-0" />
            <p className="text-[10px] font-bold text-amber-700 dark:text-amber-500 uppercase leading-relaxed">
                Post-Only (GTX): La orden solo se colocará si no cruza el spread inmediatamente. Si cruza, el bot la cancelará y re-intentará 1 tick por debajo automáticamente.
            </p>
        </div>

        <button
          onClick={handleAction}
          disabled={isLoading}
          className="w-full py-6 bg-gray-900 dark:bg-amber-500 hover:bg-black dark:hover:bg-amber-400 text-white dark:text-gray-950 rounded-[1.5rem] font-black text-xl shadow-2xl shadow-amber-500/20 transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center"
        >
          {isLoading ? <Loader2 className="w-6 h-6 animate-spin mr-3" /> : <Zap className="w-6 h-6 mr-3 fill-current" />}
          EJECUTAR ESTRATEGIA CHASE
        </button>
      </div>
    </div>
  )
}

export function MarketBuyForm({ symbol }: ActionFormProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = async () => {
    try {
      setIsLoading(true)
      await triggerManualAction(symbol, 'BUY_MIN_NOTIONAL')
      alert(`Operación Exitosa: Market Buy de $5 en ${symbol}`)
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-[2.5rem] p-10 shadow-xl border border-gray-100 dark:border-gray-800 flex flex-col items-center text-center">
      <div className="p-5 bg-emerald-100 dark:bg-emerald-900/30 rounded-3xl text-emerald-600 dark:text-emerald-400 mb-6">
        <ShoppingCart className="w-12 h-12" />
      </div>
      <h2 className="text-3xl font-black text-gray-900 dark:text-white mb-2">Market Buy ($5)</h2>
      <p className="text-gray-500 dark:text-gray-400 max-w-sm mb-10 text-sm">Ejecuta una compra inmediata a precio de mercado del monto mínimo permitido (~$5 USD) para testeo de conectividad.</p>
      
      <button
        onClick={handleAction}
        disabled={isLoading}
        className="w-full py-6 bg-emerald-600 hover:bg-emerald-500 text-white rounded-2xl font-black text-xl transition-all shadow-xl shadow-emerald-500/20 flex items-center justify-center disabled:opacity-50"
      >
        {isLoading ? <Loader2 className="w-6 h-6 animate-spin mr-3" /> : <ShoppingCart className="w-6 h-6 mr-3" />}
        COMPRAR AHORA
      </button>
    </div>
  )
}
