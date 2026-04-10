'use client'

import { useState, useEffect, useRef } from 'react'
import { simulateChase, ChaseSimulationResponse } from '@/lib/api'
import Link from 'next/link'

interface TickLog {
  id: number
  timestamp: string
  price: number
  decision: boolean
  reason: string
}

export default function ChasePlayground() {
  // Parameters
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [cooldown, setCooldown] = useState(5)
  const [threshold, setThreshold] = useState(0.0005)
  const [lastTickPrice, setLastTickPrice] = useState<number | null>(null)
  const [orderPrice, setOrderPrice] = useState<number>(50000)
  const [status, setStatus] = useState<string>('CHASING')
  const [lastUpdateTime, setLastUpdateTime] = useState<string>(new Date().toISOString())
  
  // UI State
  const [currentPrice, setCurrentPrice] = useState(50000)
  const [isAutoMode, setIsAutoMode] = useState(false)
  const [logs, setLogs] = useState<TickLog[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  const logEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // Stop auto mode if filled
  useEffect(() => {
    if (status === 'FILLED' && isAutoMode) {
      setIsAutoMode(false)
    }
  }, [status, isAutoMode])

  // Auto Tick Simulation
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isAutoMode && status === 'CHASING') {
      interval = setInterval(() => {
        const volatility = 0.001
        const change = currentPrice * (Math.random() - 0.5) * volatility
        const newPrice = currentPrice + change
        setCurrentPrice(parseFloat(newPrice.toFixed(2)))
        handleTick(newPrice)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isAutoMode, currentPrice, side, cooldown, threshold, lastTickPrice, lastUpdateTime, orderPrice, status])

  const handleTick = async (price: number) => {
    try {
      if (status === 'FILLED') return
      
      setIsLoading(true)
      const res = await simulateChase({
        current_price: price,
        order_price: orderPrice,
        last_tick_price: lastTickPrice,
        side,
        last_update_iso: lastUpdateTime,
        cooldown_seconds: cooldown,
        price_threshold: threshold,
        status: status
      })

      const newLog: TickLog = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        price: parseFloat(price.toFixed(2)),
        decision: res.status === 'FILLED' || res.should_update,
        reason: res.reason
      }

      setLogs(prev => [...prev, newLog].slice(-20))

      // Update state from response
      setStatus(res.status)
      setOrderPrice(res.order_price)
      
      if (res.should_update) {
        setLastTickPrice(price)
      }
      
      if (res.last_update_iso) {
        setLastUpdateTime(res.last_update_iso)
      }

    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const resetSimulation = () => {
    setLastTickPrice(null)
    setOrderPrice(currentPrice)
    setStatus('CHASING')
    setLastUpdateTime(new Date().toISOString())
    setLogs([])
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1 mb-2">
              ← Volver al Dashboard
            </Link>
            <h1 className="text-4xl font-bold">
              Chase Playground 🧪
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Laboratorio de simulación para la lógica de percusión de órdenes.
            </p>
          </div>
          <button 
            onClick={resetSimulation}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl font-bold hover:bg-gray-300 dark:hover:bg-gray-700 transition-all border border-gray-300 dark:border-gray-600"
          >
            Resetear Simulación
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Controls Column */}
          <div className="lg:col-span-1 space-y-6">
            {/* Parameters Card */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                ⚙️ Parámetros
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Dirección (Side)</label>
                  <div className="flex bg-gray-100 dark:bg-gray-900 p-1 rounded-xl">
                    <button 
                      onClick={() => setSide('buy')}
                      className={`flex-1 py-2 rounded-lg font-bold transition-all ${side === 'buy' ? 'bg-green-500 text-white shadow-lg' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-800'}`}
                    >
                      LONG (Buy)
                    </button>
                    <button 
                      onClick={() => setSide('sell')}
                      className={`flex-1 py-2 rounded-lg font-bold transition-all ${side === 'sell' ? 'bg-red-500 text-white shadow-lg' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-800'}`}
                    >
                      SHORT (Sell)
                    </button>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Cooldown (segundos)</label>
                    <span className="text-indigo-500 font-bold">{cooldown}s</span>
                  </div>
                  <input 
                    type="range" min="1" max="30" step="1" 
                    value={cooldown} onChange={(e) => setCooldown(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Price Threshold (%)</label>
                    <span className="text-indigo-500 font-bold">{(threshold * 100).toFixed(3)}%</span>
                  </div>
                  <input 
                    type="range" min="0.0001" max="0.005" step="0.0001" 
                    value={threshold} onChange={(e) => setThreshold(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>
              </div>
            </div>

            {/* Tick Emulator Card */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                📡 Emulador de Ticks
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Precio Actual</label>
                  <input 
                    type="number" 
                    value={currentPrice} 
                    onChange={(e) => setCurrentPrice(parseFloat(e.target.value))}
                    className="w-full p-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl font-mono text-xl text-gray-900 dark:text-white"
                  />
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleTick(currentPrice)}
                    disabled={isLoading}
                    className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-all active:scale-95 disabled:opacity-50"
                  >
                    Enviar Tick
                  </button>
                  <button 
                    onClick={() => setIsAutoMode(!isAutoMode)}
                    className={`flex-1 py-3 border-2 font-bold rounded-xl transition-all ${isAutoMode ? 'border-amber-500 text-amber-500 bg-amber-500/10' : 'border-gray-500 text-gray-500'}`}
                  >
                    {isAutoMode ? '⏹ Stop Auto' : '▶ Auto Mode'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Visualization & Logs Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status Display */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-6 rounded-2xl shadow-lg border transition-all ${status === 'FILLED' ? 'bg-green-500/10 border-green-500' : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700'}`}>
                <div className="flex justify-between items-start mb-1">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Virtual Order Price</p>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${status === 'FILLED' ? 'bg-green-500 text-white' : 'bg-indigo-500 text-white animate-pulse'}`}>
                    {status}
                  </span>
                </div>
                <p className="text-3xl font-mono font-bold">${orderPrice.toFixed(2)}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {status === 'FILLED' ? '✅ Posición abierta (FILL)' : `🎯 Nivel de entrada para ${side.toUpperCase()}`}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Simulación Activa</p>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${isAutoMode ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                  <p className="text-3xl font-bold">{isAutoMode ? 'EN VIVO' : 'PAUSA'}</p>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {status === 'FILLED' ? 'Simulación detenida por ejecución' : 'Estado del motor de simulación'}
                </p>
              </div>
            </div>

            {/* Log Panel */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden flex flex-col h-[500px]">
              <div className="p-4 bg-gray-50 dark:bg-gray-900/50 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                <h3 className="font-bold">Registro de Decisiones</h3>
                <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded text-gray-500 uppercase">Tiempo Real</span>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm">
                {logs.length === 0 && (
                  <div className="h-full flex items-center justify-center text-gray-500 italic">
                    Esperando ticks...
                  </div>
                )}
                {logs.map(log => (
                  <div key={log.id} className={`p-3 rounded-lg flex items-start gap-4 ${log.decision ? 'bg-green-500/10 border border-green-500/20' : 'bg-gray-100 dark:bg-gray-900/50'}`}>
                    <span className="text-gray-400 shrink-0">{log.timestamp}</span>
                    <span className="font-bold w-24 shrink-0 text-right">${log.price.toFixed(2)}</span>
                    <span className={`font-bold w-8 shrink-0 text-center ${log.decision ? 'text-green-500' : 'text-red-500'}`}>
                      {log.decision ? '✅' : '❌'}
                    </span>
                    <span className={`text-xs mt-1 ${log.decision ? 'text-green-600' : 'text-gray-500'}`}>
                      {log.reason}
                    </span>
                  </div>
                ))}
                <div ref={logEndRef} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
