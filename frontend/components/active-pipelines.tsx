'use client'

import React from 'react'
import { useActivePipelines, useStopPipeline } from '@/hooks/use-trades'
import { format } from 'date-fns'
import { clsx } from 'clsx'
import { ChaseInfographic } from './chase-infographic'
import { toast } from 'sonner'

export function ActivePipelines() {
  const { data: pipelines, isLoading } = useActivePipelines()
  const stopPipeline = useStopPipeline()

  if (isLoading) {
    return (
      <div className="p-8 text-center animate-pulse">
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-800 rounded-lg mx-auto mb-4" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Sincronizando procesos activos...</p>
      </div>
    )
  }

  if (!pipelines || pipelines.length === 0) {
    return (
      <div className="p-12 text-center bg-white dark:bg-gray-800/50 rounded-3xl border border-dashed border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="w-16 h-16 bg-gray-50 dark:bg-gray-900 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h4 className="text-base font-bold text-gray-900 dark:text-white mb-1">Sin Actividad de Chase</h4>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs mx-auto">No hay procesos de persecución activos en este momento. Lanza un Chase desde el Hub de Desarrollador.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <span className="p-2.5 bg-indigo-600 text-white rounded-2xl shadow-lg shadow-indigo-600/20">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </span>
          Monitoreo de Chase en Tiempo Real
        </h3>
        <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs font-bold rounded-full border border-indigo-200 dark:border-indigo-800/50">
          {pipelines.length} {pipelines.length === 1 ? 'Proceso' : 'Procesos'}
        </span>
      </div>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {pipelines.map((p) => (
          <div key={p.id} className="group relative bg-white dark:bg-gray-800 rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-xl shadow-gray-200/50 dark:shadow-none hover:border-indigo-500 dark:hover:border-indigo-500 transition-all duration-300 flex flex-col">
            {/* 
              Manual Stop Button (X) 
              Relocated to absolute top-6 right-6 with z-index to prevent overlapping issues (Repair #6)
            */}
            {p.status !== 'COMPLETED' && p.status !== 'ABORTED' && (
                <button 
                  type="button"
                  onClick={() => {
                    if (confirm('¿Detener este proceso y cancelar la orden?')) {
                      toast.promise(stopPipeline.mutateAsync(p.id), {
                        loading: 'Deteniendo proceso y cancelando órdenes...',
                        success: 'Proceso detenido correctamente',
                        error: 'Error al detener el proceso',
                      })
                    }
                  }}
                  className="absolute top-6 right-6 z-50 p-2 hover:bg-rose-50 dark:hover:bg-rose-900/20 text-gray-400 hover:text-rose-500 rounded-xl transition-all duration-200 active:scale-90 shadow-sm bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-100 dark:border-gray-700"
                  title="Detener Proceso"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
             )}

            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-black text-gray-900 dark:text-white tracking-tight">
                      {p.symbol}
                    </span>
                    <span className={clsx(
                      "text-[10px] font-bold px-2 py-0.5 rounded-md uppercase",
                      p.side === 'buy' ? "bg-emerald-100 text-emerald-600" : "bg-rose-100 text-rose-600"
                    )}>
                      {p.side}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-gray-400 mt-0.5">
                    Order ID: {p.entry_order_id || 'RECOVERY_PENDING'}
                  </span>
                </div>
              </div>
            </div>

            {/* The Dynamic Infographic */}
            <ChaseInfographic pipeline={p} />
            
            <div className="mt-4 flex items-center justify-between text-[10px] text-gray-400 border-t border-gray-50 dark:border-gray-700/50 pt-4">
               <div className="flex items-center gap-1">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Iniciado: {p.created_at ? format(new Date(p.created_at), 'HH:mm:ss') : '---'}
               </div>
               <div className="font-bold">
                  {p.sub_status?.includes('NATIVE') ? (
                    <span className="text-violet-500 bg-violet-50 dark:bg-violet-900/20 px-2 py-0.5 rounded border border-violet-100 dark:border-violet-800">
                      Chase V2 (Official Native)
                    </span>
                  ) : (
                    <span className="text-gray-500/80">
                      Adaptive OTO v5.9
                    </span>
                  )}
               </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
