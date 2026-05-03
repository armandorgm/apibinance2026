"use client"

import { useState, useEffect } from "react"
import { startChaseV2, stopChaseV2, fetchChaseV2Status, ChaseV2Status } from "@/lib/api"

interface ChaseV2WidgetProps {
  symbol: string
}

export function ChaseV2Widget({ symbol }: ChaseV2WidgetProps) {
  const [activeProcesses, setActiveProcesses] = useState<ChaseV2Status[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [amount, setAmount] = useState<number>(0.001) // Default tiny amount
  const [side, setSide] = useState<"BUY" | "SELL">("BUY")
  const [profitPc, setProfitPc] = useState<number>(0.005) // 0.5% default
  
  useEffect(() => {
    if (!symbol) return
    const fetchStatus = async () => {
      try {
        const res = await fetchChaseV2Status(symbol)
        if (res.success) {
          setActiveProcesses(res.active_processes)
        }
      } catch (err) {
        console.error("Failed to fetch Chase V2 status", err)
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [symbol])

  const handleStart = async () => {
    setIsLoading(true)
    try {
      await startChaseV2(symbol, side, amount, profitPc)
      alert(`✅ Chase V2 Started for ${symbol}`)
      // Refresh status immediately
      const res = await fetchChaseV2Status(symbol)
      if (res.success) setActiveProcesses(res.active_processes)
    } catch (error: any) {
      alert(`❌ Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStop = async (processId: number) => {
    try {
      await stopChaseV2(processId)
      alert(`✅ Stopped Process ${processId}`)
      const res = await fetchChaseV2Status(symbol)
      if (res.success) setActiveProcesses(res.active_processes)
    } catch (error: any) {
      alert(`❌ Error stopping process: ${error.message}`)
    }
  }

  if (!symbol) return null

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mt-4 text-xs font-mono">
      <div className="flex items-center justify-between mb-4 border-b border-zinc-800 pb-2">
        <h3 className="text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Chase V2 Engine (Autonomous)
        </h3>
        <span className="text-zinc-500 bg-zinc-900 px-2 py-0.5 rounded text-[10px]">
          {symbol}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-3 mb-4">
        <div>
          <label className="block text-zinc-500 mb-1 uppercase text-[10px]">Side</label>
          <select 
            className="w-full bg-zinc-900 border border-zinc-700 text-zinc-200 rounded p-1"
            value={side}
            onChange={(e) => setSide(e.target.value as "BUY" | "SELL")}
          >
            <option value="BUY">BUY</option>
            <option value="SELL">SELL</option>
          </select>
        </div>
        <div>
          <label className="block text-zinc-500 mb-1 uppercase text-[10px]">Amount</label>
          <input 
            type="number" 
            step="0.001"
            className="w-full bg-zinc-900 border border-zinc-700 text-zinc-200 rounded p-1"
            value={amount}
            onChange={(e) => setAmount(parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-zinc-500 mb-1 uppercase text-[10px]">Profit %</label>
          <input 
            type="number" 
            step="0.001"
            className="w-full bg-zinc-900 border border-zinc-700 text-zinc-200 rounded p-1"
            value={profitPc}
            onChange={(e) => setProfitPc(parseFloat(e.target.value))}
          />
        </div>
        <div className="flex items-end">
          <button 
            className={`w-full py-1.5 rounded bg-emerald-600/20 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-600/40 transition-colors uppercase font-bold text-[10px] ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={handleStart}
            disabled={isLoading || amount <= 0}
          >
            {isLoading ? 'Starting...' : 'Launch Chase'}
          </button>
        </div>
      </div>

      {activeProcesses.length > 0 && (
        <div className="mt-4">
          <h4 className="text-zinc-400 mb-2 border-b border-zinc-800 pb-1 text-[10px] uppercase">Active Processes</h4>
          <div className="space-y-2">
            {activeProcesses.map(p => (
              <div key={p.id} className="flex items-center justify-between bg-zinc-900 p-2 rounded border border-zinc-800">
                <div className="flex gap-4">
                  <span className={p.side === 'buy' ? 'text-emerald-400' : 'text-red-400'}>
                    {p.side.toUpperCase()}
                  </span>
                  <span className="text-zinc-300">{p.amount}</span>
                  <span className="text-blue-400">Ord: {p.entry_order_id?.slice(-6) || '...'}</span>
                  <span className="text-zinc-500 text-[10px] flex items-center">
                    {p.sub_status}
                  </span>
                </div>
                <button 
                  onClick={() => handleStop(p.id)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-950 px-2 py-0.5 rounded border border-red-900 transition-colors"
                >
                  Stop
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
