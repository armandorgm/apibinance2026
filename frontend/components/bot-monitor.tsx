'use client'

import React from 'react'
import { useBotStatus, useBotLogs, useBotControl } from '@/hooks/use-trades'
import { format } from 'date-fns'
import { clsx } from 'clsx'
import { ActivePipelines } from './active-pipelines'

export function BotMonitor() {
  const { data: status, isLoading: isStatusLoading } = useBotStatus()
  const { data: logs, isLoading: isLogsLoading } = useBotLogs(5)
  const { start, stop } = useBotControl()

  const isRunning = status?.is_enabled
  const lastRun = status?.last_run

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Bot Control Card */}
      <div className="lg:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700 relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg text-indigo-600 dark:text-indigo-400">
                🤖
              </span>
              Estado del Bot
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
            <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800">
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold mb-1">Última Evaluación</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {lastRun?.timestamp ? format(new Date(lastRun.timestamp), 'HH:mm:ss') : 'Esperando evaluación...'}
              </p>
            </div>

            <div className="flex gap-3">
              {!isRunning ? (
                <button
                  onClick={() => start.mutate()}
                  disabled={start.isPending}
                  className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold transition-all shadow-lg shadow-emerald-600/20 active:scale-95 disabled:opacity-50"
                >
                  {start.isPending ? 'Iniciando...' : 'Iniciar Bot'}
                </button>
              ) : (
                <button
                  onClick={() => stop.mutate()}
                  disabled={stop.isPending}
                  className="flex-1 py-3 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold transition-all shadow-lg shadow-rose-600/20 active:scale-95 disabled:opacity-50"
                >
                  {stop.isPending ? 'Deteniendo...' : 'Detener Bot'}
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Decorative background shape */}
        <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 blur-2xl rounded-full" />
      </div>

      {/* Strategy Engine Details */}
      <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
           <span className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg text-amber-600 dark:text-amber-400">
            ⚡
          </span>
          Actividad del Motor de Reglas
        </h3>
        
        <div className="space-y-3">
          {isLogsLoading ? (
            <div className="py-8 text-center text-gray-400">Cargando señales...</div>
          ) : logs?.length === 0 ? (
            <div className="py-8 text-center text-gray-400">No hay señales registradas.</div>
          ) : (
            logs?.map((log) => (
              <div key={log.id} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-900/40 rounded-xl border border-gray-100 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-600 transition-colors">
                <div className={clsx(
                  "p-2 rounded-lg text-lg",
                  log.success ? "bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600" : "bg-rose-100 dark:bg-rose-900/20 text-rose-600"
                )}>
                  {log.rule_triggered ? '🎯' : '⏳'}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-gray-900 dark:text-white text-sm">
                      {log.rule_triggered || 'Evaluación Periódica'}
                    </span>
                    <span className="text-[10px] text-gray-500 font-mono">
                      {format(new Date(log.created_at), 'HH:mm:ss')}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    {log.action_taken ? `Acción: ${log.action_taken}` : 'Sin trigger (Hold)'}
                  </p>
                  
                  {/* Exchange Interaction JSON Details */}
                  {log.action_taken === 'NEW_ORDER' && (log.exchange_request || log.exchange_response) && (
                    <div className="mt-2 space-y-2">
                       <details className="group">
                          <summary className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 cursor-pointer hover:underline list-none flex items-center gap-1">
                             <svg className="w-3 h-3 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                             </svg>
                             Ver detalles JSON del Exchange
                          </summary>
                           <div className="mt-2 p-3 bg-gray-900 rounded-lg text-[10px] font-mono text-gray-300 overflow-x-auto border border-gray-700 custom-scrollbar">
                             {!log.success && log.error_message && (
                               <div className="mb-3 border-b border-rose-900/50 pb-3">
                                 <p className="text-rose-400 mb-2 leading-none uppercase tracking-wider [font-size:9px] font-bold">Error (Execution Failure):</p>
                                 <div className="p-2 bg-rose-950/30 border border-rose-900/40 rounded text-rose-300 whitespace-pre-wrap">
                                    {log.error_message}
                                 </div>
                               </div>
                             )}
                             {log.exchange_request && (
                               <div className="mb-3 border-b border-gray-800 pb-3">
                                 <p className="text-pink-400 mb-2 leading-none uppercase tracking-wider [font-size:9px] font-bold">Request (Sent):</p>
                                 <pre className="whitespace-pre">{(() => {
                                    try {
                                      return JSON.stringify(JSON.parse(log.exchange_request), null, 2);
                                    } catch {
                                      return log.exchange_request;
                                    }
                                 })()}</pre>
                               </div>
                             )}
                             {log.exchange_response && (
                               <div>
                                 <p className="text-emerald-400 mb-2 leading-none uppercase tracking-wider [font-size:9px] font-bold">Response (Received):</p>
                                 <pre className="whitespace-pre">{(() => {
                                    try {
                                      return JSON.stringify(JSON.parse(log.exchange_response), null, 2);
                                    } catch {
                                      return log.exchange_response;
                                    }
                                 })()}</pre>
                               </div>
                             )}
                          </div>
                       </details>
                    </div>
                  )}
                </div>
                {log.params_snapshot && (
                   <div className="flex flex-col items-end gap-1">
                      <span className="px-2 py-1 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 text-[10px] rounded-md font-mono">
                          {log.params_snapshot.length > 20 ? 'params' : log.params_snapshot}
                      </span>
                   </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Active Pipelines Monitor */}
      <div className="lg:col-span-3">
        <ActivePipelines />
      </div>
    </div>
  )
}
