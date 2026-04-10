'use client'

import { useState, useEffect } from 'react'
import { fetchRepairPreview, executeRepair, RepairPreview } from '@/lib/api'
import { Wrench, Search, AlertCircle, CheckCircle2, ArrowRight, Loader2, DollarSign, Percent, ShieldAlert, Scale } from 'lucide-react'

export function RepairChaseForm() {
  const [orderId, setOrderId] = useState('7378054921') // User spec
  const [profitPc, setProfitPc] = useState(0.5)
  const [preview, setPreview] = useState<RepairPreview | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleFetchPreview = async () => {
    try {
      setIsLoading(true)
      setError(null)
      setPreview(null)
      setSuccess(null)
      const data = await fetchRepairPreview(orderId, profitPc)
      setPreview(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!preview) return
    try {
      setIsExecuting(true)
      setError(null)
      const res = await executeRepair(orderId, profitPc)
      setSuccess(`${res.message} - Cantidad Final: ${res.amount}`)
      setPreview(null)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-gray-900 rounded-[2.5rem] p-10 shadow-xl border border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-5 mb-10">
          <div className="p-4 bg-indigo-100 dark:bg-indigo-900/30 rounded-3xl text-indigo-600 dark:text-indigo-400">
            <Wrench className="w-10 h-10" />
          </div>
          <div>
            <h1 className="text-4xl font-black text-gray-900 dark:text-white tracking-tight">Reparador de Chase (Real)</h1>
            <p className="text-gray-500 dark:text-gray-400">Envía una orden real a Binance para cerrar ventas huérfanas.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 ml-2">ID de la Orden (Venta Huérfana)</label>
            <div className="relative">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-300" />
              <input
                type="text"
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                placeholder="7378054921"
                className="w-full pl-14 pr-6 py-5 bg-gray-50 dark:bg-gray-950 border border-gray-100 dark:border-gray-800 rounded-3xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none text-xl font-mono"
              />
            </div>
          </div>

          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 ml-2">Objetivo de Ganancia (%)</label>
            <div className="relative">
              <Percent className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-300" />
              <input
                type="number"
                step="0.01"
                value={profitPc}
                onChange={(e) => setProfitPc(parseFloat(e.target.value))}
                className="w-full pl-14 pr-6 py-5 bg-gray-50 dark:bg-gray-950 border border-gray-100 dark:border-gray-800 rounded-3xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none text-xl font-bold"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleFetchPreview}
          disabled={isLoading || !orderId}
          className="mt-10 w-full py-6 bg-gray-900 dark:bg-white text-white dark:text-gray-950 rounded-3xl font-black text-xl hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50 disabled:scale-100 shadow-2xl shadow-indigo-500/20"
        >
          {isLoading ? <Loader2 className="w-7 h-7 animate-spin mx-auto" /> : 'Calcular Previsualización Real'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 p-8 rounded-[2rem] flex items-start gap-5 animate-in zoom-in-95 duration-300 shadow-sm">
          <AlertCircle className="w-8 h-8 text-red-500 shrink-0" />
          <p className="text-red-700 dark:text-red-400 font-bold text-lg">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-900/20 p-8 rounded-[2rem] flex items-start gap-5 animate-in slide-in-from-top-4 duration-300 shadow-sm">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 shrink-0" />
          <div>
            <p className="text-emerald-700 dark:text-emerald-400 font-black text-2xl mb-1 tracking-tight">Ejecución Exitosa</p>
            <p className="text-emerald-600 dark:text-emerald-500 text-lg font-medium">{success}</p>
          </div>
        </div>
      )}

      {preview && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-500">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-gray-900 p-8 rounded-[2rem] border border-gray-100 dark:border-gray-800 shadow-lg">
              <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-6">Precio de Venta</p>
              <p className="text-2xl font-black text-gray-900 dark:text-white font-mono">{preview.original_price.toFixed(6)}</p>
              <p className="text-[10px] text-gray-400 mt-2 font-bold uppercase tracking-wider">Cant: {preview.amount}</p>
            </div>
            
            <div className="flex items-center justify-center">
              <ArrowRight className="w-8 h-8 text-indigo-500" />
            </div>

            <div className="bg-indigo-600 p-8 rounded-[2rem] shadow-xl relative overflow-hidden">
              <p className="text-[10px] font-black text-indigo-200 uppercase tracking-widest mb-6">Precio de Compra Final</p>
              <p className="text-2xl font-black text-white font-mono">{preview.target_buy_price.toFixed(6)}</p>
              <p className="text-[10px] text-indigo-200 mt-2 font-bold uppercase tracking-wider">🎯 {preview.profit_percentage}% Profit</p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-900 rounded-[2.5rem] p-10 border border-gray-100 dark:border-gray-800 shadow-2xl">
            <div className="flex items-center justify-between mb-10">
              <h3 className="text-2xl font-black flex items-center gap-3 tracking-tight">
                Plan de Ejecución Real
              </h3>
              {preview.needs_scaling && (
                <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-500 border border-amber-200 dark:border-amber-900/30 rounded-2xl text-[10px] font-black uppercase tracking-widest">
                  <Scale className="w-4 h-4" />
                  Auto-Escalado a $5.05 USD
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-10">
              <div className="space-y-4">
                 <div className="flex justify-between items-center py-4 border-b border-gray-50 dark:border-gray-800">
                    <span className="text-gray-400 font-bold uppercase text-[10px] tracking-widest">Símbolo</span>
                    <span className="font-mono font-black text-lg">{preview.symbol}</span>
                </div>
                <div className="flex justify-between items-center py-4 border-b border-gray-50 dark:border-gray-800">
                    <span className="text-gray-400 font-bold uppercase text-[10px] tracking-widest">Cantidad a Comprar</span>
                    <span className={`font-black text-xl ${preview.needs_scaling ? 'text-amber-500' : ''}`}>
                      {preview.needs_scaling ? preview.adjusted_amount?.toFixed(0) : preview.amount}
                    </span>
                </div>
                <div className="flex justify-between items-center py-4 border-b border-gray-50 dark:border-gray-800">
                    <span className="text-gray-400 font-bold uppercase text-[10px] tracking-widest">Valor Nocional</span>
                    <span className="font-bold text-gray-600 dark:text-gray-400">
                      ${((preview.needs_scaling ? preview.adjusted_amount || 0 : preview.amount) * preview.target_buy_price).toFixed(2)} USD
                    </span>
                </div>
              </div>
              
              <div className="p-8 rounded-3xl bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-900/20">
                <div className="flex items-center gap-3 mb-4 text-indigo-600 dark:text-indigo-400">
                  <ShieldAlert className="w-6 h-6" />
                  <p className="font-black uppercase text-xs tracking-widest">Seguridad de Ejecución</p>
                </div>
                <ul className="space-y-3 text-[11px] text-indigo-700 dark:text-indigo-300 font-medium">
                  <li className="flex gap-2"><span>•</span> <span>Se enviará una orden <b>Limit</b> real directo al exchange.</span></li>
                  <li className="flex gap-2"><span>•</span> <span>Sin "Reduce-Only" para evitar rechazos por tu posición Long.</span></li>
                  {preview.needs_scaling && (
                    <li className="flex gap-2 text-amber-700 dark:text-amber-500 font-bold">
                      <span>•</span> <span>Se aumentó la cantidad a comprar para superar el mínimo de $5 de Binance.</span>
                    </li>
                  )}
                </ul>
              </div>
            </div>

            <button
              onClick={handleExecute}
              disabled={isExecuting}
              className="w-full py-8 bg-indigo-600 hover:bg-indigo-500 text-white rounded-[1.5rem] font-black text-2xl shadow-xl shadow-indigo-500/30 transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center"
            >
              {isExecuting ? <Loader2 className="w-8 h-8 animate-spin mr-3" /> : <CheckCircle2 className="w-8 h-8 mr-3" />}
              {isExecuting ? 'Ejecutando en Binance...' : 'Confirmar y Colocar Orden Limit'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
