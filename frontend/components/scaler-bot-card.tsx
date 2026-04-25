'use client'

import React, { useState } from 'react'
import { useScalerStatus, useScalerControl } from '@/hooks/use-trades'
import { format } from 'date-fns'
import { clsx } from 'clsx'

interface ScalerBotCardProps {
  symbol: string
}

export function ScalerBotCard({ symbol }: ScalerBotCardProps) {
  const { data: status, isLoading } = useScalerStatus()
  const { enable, disable } = useScalerControl()

  const [profitPc, setProfitPc] = useState(0.005)
  const [interval, setIntervalHours] = useState(8.0)

  const isRunning = status?.is_enabled
  const lastExec = status?.last_execution_at

  const handleToggle = () => {
    if (isRunning) {
      disable.mutate()
    } else {
      enable.mutate({ 
        symbol, 
        defaultProfitPc: profitPc, 
        intervalHours: interval 
      })
    }
  }

  // Update local state when data loads (only if not running to avoid jumpy UI)
  React.useEffect(() => {
    if (status && !isRunning) {
      setProfitPc(status.default_profit_pc)
      setIntervalHours(status.interval_hours)
    }
  }, [status, isRunning])

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700 relative overflow-hidden">
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg text-purple-600 dark:text-purple-400">
              ⚖️
            </span>
            Bot C: Scaler
          </h3>
          <div className="flex items-center gap-2">
            <span className={clsx(
              "w-3 h-3 rounded-full",
              isRunning ? "bg-emerald-500 animate-pulse" : "bg-gray-400"
            )} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {isRunning ? 'Activo' : 'Inactivo'}
            </span>
          </div>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800">
              <p className="text-[10px] text-gray-500 dark:text-gray-400 uppercase font-bold mb-1">Profit Fallback</p>
              {isRunning ? (
                <p className="text-sm font-mono text-gray-900 dark:text-white">{(status?.default_profit_pc * 100).toFixed(2)}%</p>
              ) : (
                <div className="flex items-center gap-1">
                  <input 
                    type="number" 
                    step="0.001"
                    value={profitPc}
                    onChange={(e) => setProfitPc(parseFloat(e.target.value))}
                    className="w-full bg-transparent border-none p-0 text-sm font-mono focus:ring-0 text-gray-900 dark:text-white"
                  />
                </div>
              )}
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800">
              <p className="text-[10px] text-gray-500 dark:text-gray-400 uppercase font-bold mb-1">Intervalo (h)</p>
              {isRunning ? (
                <p className="text-sm font-mono text-gray-900 dark:text-white">{status?.interval_hours}h</p>
              ) : (
                <input 
                  type="number" 
                  step="0.5"
                  value={interval}
                  onChange={(e) => setIntervalHours(parseFloat(e.target.value))}
                  className="w-full bg-transparent border-none p-0 text-sm font-mono focus:ring-0 text-gray-900 dark:text-white"
                />
              )}
            </div>
          </div>

          {isRunning && (
            <div className="p-3 bg-indigo-50/50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100/50 dark:border-indigo-900/30">
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] text-indigo-600 dark:text-indigo-400 uppercase font-bold">Último Ciclo</span>
                <span className="text-[10px] font-mono text-indigo-500">#{status?.cycles_executed || 0}</span>
              </div>
              <div className="flex justify-between items-end">
                <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {lastExec ? format(new Date(lastExec), 'MMM d, HH:mm') : 'Nunca'}
                </p>
                {status?.last_cycle_side && (
                  <span className={clsx(
                    "text-[10px] px-1.5 py-0.5 rounded font-bold uppercase",
                    status.last_cycle_side === 'buy' ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
                  )}>
                    {status.last_cycle_side}
                  </span>
                )}
              </div>
            </div>
          )}

          <button
            onClick={handleToggle}
            disabled={enable.isPending || disable.isPending}
            className={clsx(
              "w-full py-3 rounded-xl font-bold transition-all shadow-lg active:scale-95 disabled:opacity-50",
              isRunning 
                ? "bg-rose-600 hover:bg-rose-700 text-white shadow-rose-600/20" 
                : "bg-purple-600 hover:bg-purple-700 text-white shadow-purple-600/20"
            )}
          >
            {enable.isPending || disable.isPending 
              ? 'Procesando...' 
              : isRunning ? 'Detener Scaler' : 'Activar Scaler'}
          </button>
        </div>
      </div>
      
      {/* Decorative background shape */}
      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-gradient-to-br from-purple-500/10 to-pink-500/10 blur-2xl rounded-full" />
    </div>
  )
}
