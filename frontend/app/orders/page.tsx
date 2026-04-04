'use client'

import { useState } from 'react'
import { useOpenOrders, useFailedOrders } from '@/hooks/use-trades'
import { format } from 'date-fns'
import { formatPrice, formatAmount } from '@/lib/utils'
import Link from 'next/link'

export default function OrdersPage() {
  const [activeTab, setActiveTab] = useState<'live' | 'failed'>('live')
  const [showOnlyBot, setShowOnlyBot] = useState(true)
  
  const { data: openOrders, isLoading: loadingOpen } = useOpenOrders()
  const { data: failedOrders, isLoading: loadingFailed } = useFailedOrders()

  const filteredOrders = showOnlyBot 
    ? openOrders?.filter(o => o.is_bot_logged) 
    : openOrders

  return (
    <main className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <Link href="/" className="text-sm text-indigo-600 dark:text-indigo-400 font-medium hover:underline mb-2 block">
              ← Volver al Dashboard
            </Link>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Monitor de Órdenes
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Seguimiento en vivo del libro de órdenes y registro de errores de ejecución.
            </p>
          </div>
        </div>

        {/* Tabs and Controls */}
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex bg-white dark:bg-gray-800 p-1 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('live')}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                activeTab === 'live' 
                ? 'bg-indigo-600 text-white shadow-md' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
            >
              Órdenes Activas ({openOrders?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('failed')}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                activeTab === 'failed' 
                ? 'bg-indigo-600 text-white shadow-md' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
            >
              Intentos Fallidos ({failedOrders?.length || 0})
            </button>
          </div>

          {activeTab === 'live' && (
            <div className="flex items-center gap-3 bg-white dark:bg-gray-800 px-4 py-2 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Solo órdenes del Bot
              </label>
              <button
                onClick={() => setShowOnlyBot(!showOnlyBot)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                    showOnlyBot ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    showOnlyBot ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          {activeTab === 'live' ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Símbolo / Hora</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Tipo / Lado</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Precio</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cantidad</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Estado</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Origen</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {loadingOpen ? (
                    <tr><td colSpan={6} className="px-6 py-12 text-center text-gray-400">Cargando libro de órdenes...</td></tr>
                  ) : filteredOrders?.length === 0 ? (
                    <tr><td colSpan={6} className="px-6 py-12 text-center text-gray-400">No se encontraron órdenes abiertas.</td></tr>
                  ) : (
                    filteredOrders?.map((order) => (
                      <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-bold text-gray-900 dark:text-white">{order.symbol}</div>
                          <div className="text-[10px] text-gray-400">{format(new Date(order.datetime), 'dd/MM HH:mm:ss')}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex flex-col gap-1">
                            {order.is_algo ? (
                              <span className="flex items-center gap-1.5 text-[10px] text-purple-600 dark:text-purple-400 font-bold bg-purple-50 dark:bg-purple-900/30 px-2 py-0.5 rounded border border-purple-100 dark:border-purple-800 w-fit">
                                🤖 ALGO SERVICE (TP/SL)
                              </span>
                            ) : (
                                <span className="flex items-center gap-1.5 text-[10px] text-blue-600 dark:text-blue-400 font-bold bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded border border-blue-100 dark:border-blue-800 w-fit">
                                ⚖️ STANDARD (LIMIT)
                              </span>
                            )}
                            <div className="flex flex-wrap items-center gap-1">
                              <span className="text-xs font-semibold px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 uppercase">
                                {order.type}
                              </span>
                              <span className={`text-xs font-bold ${order.side === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                                {order.side.toUpperCase()}
                              </span>
                              {order.is_algo && order.conditional_kind === 'take_profit' && order.side === 'sell' && (
                                <span className="text-[10px] font-bold text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/40 px-1.5 py-0.5 rounded border border-amber-200 dark:border-amber-800">
                                  TP → cierra LONG
                                </span>
                              )}
                              {order.is_algo && order.conditional_kind === 'stop_loss' && order.side === 'sell' && (
                                <span className="text-[10px] font-bold text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/30 px-1.5 py-0.5 rounded border border-rose-200 dark:border-rose-800">
                                  SL → cierra LONG
                                </span>
                              )}
                              {order.position_side && (
                                <span className="text-[10px] text-gray-500 dark:text-gray-400 font-mono">
                                  pos: {order.position_side.toUpperCase()}
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {formatPrice(order.price)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900 dark:text-white font-medium">{formatAmount(order.amount)}</div>
                            <div className="text-[10px] text-gray-400">Restante: {formatAmount(order.remaining)}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                            {order.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {order.is_bot_logged ? (
                            <span className="flex items-center gap-1.5 text-xs text-indigo-600 dark:text-indigo-400 font-bold bg-indigo-50 dark:bg-indigo-900/30 px-2 py-1 rounded-lg border border-indigo-100 dark:border-indigo-800">
                              <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
                              Bot Logged
                            </span>
                          ) : (
                            <span className="text-xs text-gray-400 italic">Manual / Externo</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Hora / Símbolo</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Regla / Acción</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider w-1/2">Detalle del Error (API Exchange)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {loadingFailed ? (
                    <tr><td colSpan={3} className="px-6 py-12 text-center text-gray-400">Cargando historial de fallos...</td></tr>
                  ) : failedOrders?.length === 0 ? (
                    <tr><td colSpan={3} className="px-6 py-12 text-center text-gray-400">No hay errores registrados recientemente.</td></tr>
                  ) : (
                    failedOrders?.map((signal) => (
                      <tr key={signal.id} className="hover:bg-red-50/30 dark:hover:bg-red-900/10 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-bold text-gray-900 dark:text-white">{format(new Date(signal.created_at), 'HH:mm:ss')}</div>
                          <div className="text-[10px] text-gray-400">{signal.symbol}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-xs font-semibold text-gray-600 dark:text-gray-300">{signal.rule_triggered}</div>
                          <div className="text-xs text-red-500 font-bold">{signal.action_taken}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 p-3 rounded-xl border border-red-100 dark:border-red-900/50 text-xs font-mono break-all line-clamp-3 hover:line-clamp-none transition-all cursor-help" title="Haz clic para ver completo">
                            {signal.error_message || signal.exchange_response || "Desconocido"}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
