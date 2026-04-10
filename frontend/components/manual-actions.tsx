'use client'

import { useState } from 'react'
import { triggerManualAction } from '@/lib/api'
import { Loader2, Zap, ShoppingCart, Settings2 } from 'lucide-react'

interface ManualActionsProps {
  symbol: string
}

export function ManualActions({ symbol }: ManualActionsProps) {
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [amount, setAmount] = useState('20')
  const [isLoading, setIsLoading] = useState(false)
  
  // Custom Parameters
  const [useCustomCooldown, setUseCustomCooldown] = useState(false)
  const [cooldown, setCooldown] = useState(5)
  
  const [useCustomThreshold, setUseCustomThreshold] = useState(false)
  const [threshold, setThreshold] = useState(0.0005)

  const handleAction = async (actionType: string) => {
    try {
      setIsLoading(true)
      await triggerManualAction(symbol, actionType, {
        side,
        amount: parseFloat(amount),
        cooldown: useCustomCooldown ? cooldown : undefined,
        threshold: useCustomThreshold ? threshold : undefined,
      })
      alert(`Éxito: Acción ${actionType} iniciada en ${symbol}`)
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-100 dark:border-gray-700">
      <div className="p-6 border-b border-gray-100 dark:border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
          <Zap className="w-5 h-5 text-amber-500 fill-amber-500" />
          Operaciones Manuales
        </h2>
      </div>
      <div className="p-6 space-y-6">
        {/* Side Selector */}
        <div className="grid grid-cols-2 gap-3 p-1 bg-gray-100 dark:bg-gray-900 rounded-xl">
          <button
            className={`py-2 px-4 rounded-lg font-bold transition-all ${side === 'buy' ? 'bg-green-600 text-white shadow-md' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-800'}`}
            onClick={() => setSide('buy')}
          >
            LONG (Buy)
          </button>
          <button
            className={`py-2 px-4 rounded-lg font-bold transition-all ${side === 'sell' ? 'bg-red-600 text-white shadow-md' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-800'}`}
            onClick={() => setSide('sell')}
          >
            SHORT (Sell)
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Main Params */}
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs uppercase font-bold text-gray-500 dark:text-gray-400">Monto (USD)</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full pl-8 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-950 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Advanced Params */}
          <div className="space-y-4 p-4 border border-gray-100 dark:border-gray-700 rounded-2xl bg-gray-50 dark:bg-gray-900/50">
            <h4 className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase">
              <Settings2 className="w-3 h-3" />
              Parámetros de Chase
            </h4>
            
            {/* Cooldown */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-gray-700 dark:text-gray-300">Cooldown ({cooldown}s)</label>
                <div 
                  className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${useCustomCooldown ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'}`}
                  onClick={() => setUseCustomCooldown(!useCustomCooldown)}
                >
                  <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${useCustomCooldown ? 'left-6' : 'left-1'}`} />
                </div>
              </div>
              {useCustomCooldown && (
                <input
                  type="range"
                  min="0"
                  max="30"
                  step="1"
                  value={cooldown}
                  onChange={(e) => setCooldown(parseInt(e.target.value))}
                  className="w-full accent-indigo-600"
                />
              )}
            </div>

            {/* Threshold */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-gray-700 dark:text-gray-300">Threshold ({(threshold * 100).toFixed(3)}%)</label>
                <div 
                  className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${useCustomThreshold ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'}`}
                  onClick={() => setUseCustomThreshold(!useCustomThreshold)}
                >
                  <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${useCustomThreshold ? 'left-6' : 'left-1'}`} />
                </div>
              </div>
              {useCustomThreshold && (
                <input
                  type="range"
                  min="0.0001"
                  max="0.005"
                  step="0.0001"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-indigo-600"
                />
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
          <button
            disabled={isLoading}
            className="flex items-center justify-center h-14 rounded-2xl font-bold text-white transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:scale-100 bg-gradient-to-r from-indigo-600 to-violet-600 shadow-lg shadow-indigo-500/20"
            onClick={() => handleAction('ADAPTIVE_OTO')}
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            ) : (
              <Zap className="mr-2 h-5 w-5 fill-white" />
            )}
            Chase Entry (Post-Only)
          </button>
          
          <button
            onClick={() => handleAction('BUY_MIN_NOTIONAL')}
            disabled={isLoading}
            className="flex items-center justify-center h-14 rounded-2xl font-bold border-2 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-all disabled:opacity-50"
          >
            <ShoppingCart className="mr-2 h-5 w-5" />
            Market Buy ($5)
          </button>
        </div>
      </div>
    </div>
  )
}
