'use client'

import { useEffect, useState } from 'react'
import { triggerManualAction, watchSymbol } from '@/lib/api'
import { Zap, ShoppingCart, Loader2, DollarSign, Settings2, ShieldAlert } from 'lucide-react'

import { toast } from 'sonner'

import { useNotifications } from '../notification-provider'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface ActionFormProps {
  symbol: string
}

export function ChaseEntryForm({ symbol: initialSymbol }: ActionFormProps) {
  const [symbol, setSymbol] = useState(initialSymbol)
  const [serverSymbol, setServerSymbol] = useState(initialSymbol) // Normalized symbol from backend
  const { prices, connectionStatus } = useNotifications()
  
  // V5.9.21: Direct dual-key lookup (Failsafe)
  const getTicker = () => {
    // Attempt lookup by CCXT server symbol or raw Binance symbol directly
    return prices[serverSymbol] || prices[symbol] || {}
  }

  const ticker = getTicker()
  
  // V5.9.8: Activar seguimiento con normalización de servidor
  useEffect(() => {
    if (symbol) {
      watchSymbol(symbol)
        .then(res => {
          if (res.ccxt_symbol) {
            setServerSymbol(res.ccxt_symbol)
            console.log(`[WATCH] Server normalized ${symbol} -> ${res.ccxt_symbol}`)
          }
        })
        .catch(err => console.error("Watch failed:", err))
    }
  }, [symbol])

  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [amount, setAmount] = useState('20')
  const [isLoading, setIsLoading] = useState(false)
  const [threshold, setThreshold] = useState(0.0005)
  const [profitPc, setProfitPc] = useState(0.005)
  const [useV2, setUseV2] = useState(true)

  const handleAction = async () => {
    setIsLoading(true)
    
    const actionType = useV2 ? 'ADAPTIVE_OTO_V2' : 'ADAPTIVE_OTO'

    toast.promise(
      triggerManualAction(symbol, actionType, {
        side,
        amount: parseFloat(amount),
        threshold,
        profit_pc: actionType === 'ADAPTIVE_OTO_V2' ? profitPc : undefined
      }),
      {
        loading: `Iniciando estrategia ${useV2 ? 'V2 (Native)' : 'V1 (CCXT)'}...`,
        success: () => `Éxito: Chase ${useV2 ? 'V2' : 'V1'} iniciado en ${symbol}`,
        error: (error) => {
          console.error("[CHASE ACTION ERROR]", error)
          return `Error: ${error.message || 'Error desconocido'}`
        },
        finally: () => setIsLoading(false)
      }
    )
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

      {/* Real-time Price Display */}
      <div className="mb-8 p-6 bg-gray-50 dark:bg-gray-950 border border-gray-100 dark:border-gray-800 rounded-[2rem] flex items-center justify-between">
        <div className="space-y-1">
          <label className="text-[10px] font-black uppercase tracking-tighter text-gray-400">Current Price (Mid)</label>
          <div className="text-2xl font-black text-gray-900 dark:text-white font-mono tracking-tight">
            {ticker.last ? ticker.last.toFixed(symbol.includes('PEPE') ? 8 : 4) : '---'}
          </div>
        </div>
        <div className="flex gap-4">
          <div className="text-right">
            <div className="text-[9px] font-bold text-green-500 uppercase flex items-center justify-end gap-1">
              <TrendingUp className="w-2 h-2" /> Bid
            </div>
            <div className="text-sm font-bold font-mono">{ticker.bid?.toFixed(symbol.includes('PEPE') ? 8 : 4) || '---'}</div>
          </div>
          <div className="text-right">
            <div className="text-[9px] font-bold text-red-500 uppercase flex items-center justify-end gap-1">
              <TrendingDown className="w-2 h-2" /> Ask
            </div>
            <div className="text-sm font-bold font-mono">{ticker.ask?.toFixed(symbol.includes('PEPE') ? 8 : 4) || '---'}</div>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        {/* Symbol Selector inside form for robustness */}
        <div className="space-y-2">
            <label className="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Símbolo Activo</label>
            <select 
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full px-6 py-4 bg-gray-50 dark:bg-gray-950 border border-gray-100 dark:border-gray-800 rounded-3xl font-bold text-gray-900 dark:text-white focus:ring-4 focus:ring-amber-500/10 outline-none transition-all"
            >
              <option value="1000PEPEUSDC">1000PEPEUSDC</option>
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
            </select>
        </div>

        <div className="grid grid-cols-2 gap-4 p-1.5 bg-gray-50 dark:bg-gray-950 rounded-[1.5rem] border border-gray-100 dark:border-gray-800">
          <button
            onClick={() => setSide('buy')}
            className={`py-4 rounded-2xl font-black text-sm transition-all ${side === 'buy' ? 'bg-green-600 text-white shadow-xl scale-[1.02]' : 'text-gray-400 hover:text-gray-600'}`}
          >
            LONG POSITION
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

          <div className="space-y-4">
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

            {useV2 && (
              <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                <label className="text-xs font-black uppercase tracking-widest text-indigo-400 ml-1 flex justify-between">
                  Profit Target % (V2)
                  <span className="text-indigo-500">{(profitPc * 100).toFixed(1)}%</span>
                </label>
                <div className="px-6 py-5 bg-indigo-50/30 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-800 rounded-3xl">
                  <input
                    type="range"
                    min="0.001"
                    max="0.05"
                    step="0.001"
                    value={profitPc}
                    onChange={(e) => setProfitPc(parseFloat(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-amber-50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-900/20 flex gap-4">
            <ShieldAlert className="w-6 h-6 text-amber-600 shrink-0" />
            <p className="text-[10px] font-bold text-amber-700 dark:text-amber-500 uppercase leading-relaxed">
                Post-Only (GTX): La orden solo se colocará si no cruza el spread inmediatamente. Si cruza, el bot la cancelará y re-intentará 1 tick por debajo automáticamente.
            </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => { setUseV2(false); setTimeout(handleAction, 50); }}
            disabled={isLoading}
            className="py-5 bg-gray-800 hover:bg-black text-white rounded-2xl font-black text-lg transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center border border-gray-700"
          >
            {isLoading && !useV2 ? <Loader2 className="w-5 h-5 animate-spin mr-3" /> : <Zap className="w-5 h-5 mr-3" />}
            CHASE V1 (CCXT)
          </button>

          <button
            onClick={() => { setUseV2(true); setTimeout(handleAction, 50); }}
            disabled={isLoading}
            className="py-5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-black text-lg shadow-xl shadow-indigo-500/20 transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center"
          >
            {isLoading && useV2 ? <Loader2 className="w-5 h-5 animate-spin mr-3" /> : <Zap className="w-5 h-5 mr-3 fill-current" />}
            CHASE V2 (NATIVE)
          </button>
        </div>
      </div>
    </div>
  )
}

export function MarketBuyForm({ symbol }: ActionFormProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = async () => {
    setIsLoading(true)
    
    toast.promise(
      triggerManualAction(symbol, 'BUY_MIN_NOTIONAL'),
      {
        loading: 'Ejecutando Market Buy ($5)...',
        success: () => `Operación Exitosa: Market Buy de $5 en ${symbol}`,
        error: (error) => `Error: ${error.message || 'Error desconocido'}`,
        finally: () => setIsLoading(false)
      }
    )
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
