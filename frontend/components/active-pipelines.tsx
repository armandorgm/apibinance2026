'use client'

import React from 'react'
import { useActivePipelines, useStopPipeline } from '@/hooks/use-trades'
import { format } from 'date-fns'
import { clsx } from 'clsx'

export function ActivePipelines() {
  const { data: pipelines, isLoading } = useActivePipelines()
  const stopPipeline = useStopPipeline()

  if (isLoading) {
    return <div className="p-4 text-center text-gray-500">Cargando procesos activos...</div>
  }

  if (!pipelines || pipelines.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 dark:bg-gray-900/20 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800">
        <p className="text-sm text-gray-500 dark:text-gray-400">No hay procesos de persecución (Chase) activos.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
        <span className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg text-indigo-600 dark:text-indigo-400">
          🔄
        </span>
        Procesos en Curso (Active Chases)
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {pipelines.map((p) => (
          <div key={p.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-all">
            <div className="flex justify-between items-start mb-3">
              <div>
                <span className="text-xs font-bold px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full uppercase tracking-wider">
                  {p.symbol}
                </span>
                <h4 className="text-sm font-bold text-gray-900 dark:text-white mt-1">
                  ID: {p.entry_order_id || 'N/A'}
                </h4>
              </div>
              <div className="flex items-center gap-2">
                 <span className={clsx(
                  "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                  p.status === 'CHASING' ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600" : "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600"
                )}>
                  {p.status}
                </span>
                <button 
                  onClick={() => {
                    if (confirm('¿Detener este proceso y cancelar la orden?')) {
                      stopPipeline.mutate(p.id)
                    }
                  }}
                  className="p-1 hover:bg-rose-100 dark:hover:bg-rose-900/30 text-rose-500 rounded transition-colors"
                  title="Detener Proceso"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                <p className="text-gray-500 dark:text-gray-400 uppercase font-semibold">Último Precio</p>
                <p className="text-gray-900 dark:text-white font-mono">{p.last_tick_price?.toFixed(2) || '---'}</p>
              </div>
              <div className="p-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                <p className="text-gray-500 dark:text-gray-400 uppercase font-semibold">Iniciado</p>
                <p className="text-gray-900 dark:text-white">{p.created_at ? format(new Date(p.created_at), 'HH:mm:ss') : '---'}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
