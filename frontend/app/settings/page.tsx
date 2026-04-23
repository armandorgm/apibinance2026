'use client'

import React, { useState, useEffect } from 'react'
import { useBotConfig, useUpdateBotConfig } from '@/hooks/use-trades'
import { useRouter } from 'next/navigation'

export default function SettingsPage() {
  const { data: config, isLoading } = useBotConfig()
  const updateConfig = useUpdateBotConfig()
  const router = useRouter()

  const [symbol, setSymbol] = useState('')
  const [interval, setInterval] = useState(60)
  const [tradeAmount, setTradeAmount] = useState(5.01)
  const [isEnabled, setIsEnabled] = useState(false)

  // Sync internal state with fetched data
  useEffect(() => {
    if (config) {
      setSymbol(config.symbol)
      setInterval(config.interval)
      setTradeAmount(config.trade_amount ?? 5.01)
      setIsEnabled(config.is_enabled)
    }
  }, [config])

  const handleSave = () => {
    updateConfig.mutate({
      symbol,
      interval,
      trade_amount: tradeAmount,
      is_enabled: isEnabled,
    }, {
      onSuccess: () => {
        alert('Configuración guardada correctamente.')
      },
      onError: (error) => {
        alert(`Error al guardar: ${error.message}`)
      }
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-600">
        Cargando configuración...
      </div>
    )
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900">
      <div className="max-w-3xl mx-auto">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Configuración del Bot</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Controla el comportamiento autónomo del motor de trading.
            </p>
          </div>
          <button 
            onClick={() => router.push('/')}
            className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-indigo-600 transition-colors"
          >
            ← Volver al Dashboard
          </button>
        </header>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="p-8 space-y-6">
            {/* Symbol Config */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                Símbolo de Trading
              </label>
              <input 
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="Ej: BTC/USDT o 1000PEPEUSDC"
                className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
              />
              <p className="text-xs text-gray-400">
                Asegúrate de usar el formato correcto del exchange (ej. 1000PEPEUSDC para futuros de PEPE).
              </p>
            </div>

            {/* Interval Config */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                Intervalo de Evaluación (segundos)
              </label>
              <input 
                type="number"
                value={interval}
                onChange={(e) => setInterval(parseInt(e.target.value))}
                min={1}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
              />
              <p className="text-xs text-gray-400">
                Tiempo de espera entre cada ejecución del motor de reglas.
              </p>
            </div>

            {/* Trade Amount Config */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                Monto de Inversión (Notional USDC)
              </label>
              <input 
                type="number"
                value={tradeAmount}
                onChange={(e) => setTradeAmount(parseFloat(e.target.value))}
                min={0.0001}
                step="0.0001"
                className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
              />
              <p className="text-xs text-amber-500">
                💡 En Binance Futures, para evitar el error "min notional", este valor debe superar los 5 USD. El sistema calculará automáticamente la cantidad real de contratos dividiendo este monto por el precio en vivo. (Nota: tu apalancamiento actuará normalmente).
              </p>
            </div>

            {/* Enable/Disable Toggle */}
            <div className="flex items-center justify-between py-4 border-t border-gray-50 dark:border-gray-700">
              <div>
                <h4 className="font-bold text-gray-900 dark:text-white">Estado del Bot</h4>
                <p className="text-xs text-gray-500 dark:text-gray-400">Habilita o deshabilita la ejecución automática.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer" 
                  checked={isEnabled}
                  onChange={(e) => setIsEnabled(e.target.checked)}
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>

          <div className="p-6 bg-gray-50 dark:bg-gray-900/40 border-t border-gray-100 dark:border-gray-700 flex justify-end">
            <button
              onClick={handleSave}
              disabled={updateConfig.isPending}
              className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-xl font-bold shadow-lg shadow-indigo-600/20 transition-all active:scale-95"
            >
              {updateConfig.isPending ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
