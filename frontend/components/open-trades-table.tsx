'use client'

import React from 'react'
import { Trade } from '@/lib/api'
import { format } from 'date-fns'
import { formatPrice, formatAmount } from '@/lib/utils'
import { Zap, Clock, ShieldCheck, ArrowRightCircle, LayersIcon, Activity } from 'lucide-react'

interface OpenTradesTableProps {
  trades: Trade[]
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-wider border border-emerald-500/20">
      <span className="relative flex h-1.5 w-1.5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
      </span>
      {status || 'PENDING'}
    </span>
  )
}

function SourceBadge({ originator }: { originator: string | undefined }) {
  const isBot = originator === 'BOT_APP' || originator === 'AUTO_ALGO'
  return (
    <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-tighter ${
      isBot 
        ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' 
        : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
    }`}>
      {isBot ? 'BOT' : 'MANUAL'}
    </span>
  )
}

export function OpenTradesTable({ trades }: OpenTradesTableProps) {
  // Filter for pending orders only
  const openOrders = trades.filter(t => t.is_pending)

  if (openOrders.length === 0) {
    return (
      <div className="mb-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700/50">
        <div className="p-6 border-b border-gray-100 dark:border-gray-700/50 flex items-center justify-between">
           <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/10 rounded-lg">
              <LayersIcon className="w-5 h-5 text-amber-500" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Órdenes Abiertas</h2>
          </div>
          <span className="text-xs font-medium text-gray-400">0 órdenes activas</span>
        </div>
        <div className="p-12 text-center text-gray-500 dark:text-gray-400 italic text-sm">
          No hay órdenes pendientes para este par.
        </div>
      </div>
    )
  }

  return (
    <div className="mb-8 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-700/50 transition-all hover:shadow-indigo-500/5">
      <div className="p-6 border-b border-gray-100 dark:border-gray-700/50 bg-gradient-to-r from-transparent via-transparent to-indigo-500/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 rounded-lg">
            <Activity className="w-5 h-5 text-indigo-500" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Órdenes Abiertas</h2>
            <p className="text-[10px] text-gray-500 dark:text-gray-400 uppercase tracking-widest font-semibold">Active & Conditional Orders</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-1.5 px-3 py-1 bg-gray-50 dark:bg-gray-900/50 rounded-full border border-gray-100 dark:border-gray-700/50">
             <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
             <span className="text-[11px] font-bold text-gray-600 dark:text-gray-300">{openOrders.length} ACTIVAS</span>
           </div>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50/50 dark:bg-gray-900/30 text-[10px] text-gray-400 dark:text-gray-500 uppercase tracking-wider font-bold">
              <th className="px-6 py-4 text-left">Tipo / Origen</th>
              <th className="px-6 py-4 text-left">Lado</th>
              <th className="px-6 py-4 text-left">Precio</th>
              <th className="px-6 py-4 text-left">Cantidad</th>
              <th className="px-6 py-4 text-left">Estado</th>
              <th className="px-6 py-4 text-right">Fecha / Hora</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
            {openOrders.map((order) => (
              <tr key={order.id} className="group hover:bg-indigo-50/20 dark:hover:bg-indigo-900/10 transition-all duration-200">
                <td className="px-6 py-5">
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center gap-2">
                       <span className="text-sm font-black text-gray-900 dark:text-white">
                        {order.order_type || 'LIMIT'}
                      </span>
                      <SourceBadge originator={order.originator} />
                    </div>
                    <span className="text-[9px] font-mono text-gray-400 dark:text-gray-500 truncate max-w-[100px]">
                      ID: #{order.entry_order_id?.slice(-8) || order.id}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-5">
                   <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-bold uppercase ${
                    order.entry_side.toLowerCase() === 'buy' 
                      ? 'text-emerald-500 bg-emerald-500/5' 
                      : 'text-rose-500 bg-rose-500/5'
                  }`}>
                    {order.entry_side.toLowerCase() === 'buy' ? <Zap className="w-3 h-3" /> : <ArrowRightCircle className="w-3 h-3 rotate-90" />}
                    {order.entry_side}
                  </div>
                </td>
                <td className="px-6 py-5">
                   <div className="flex flex-col">
                    <span className="text-sm font-bold text-gray-900 dark:text-white font-mono">
                      {formatPrice(order.entry_price)}
                    </span>
                    <span className="text-[10px] text-gray-400 uppercase font-medium">Marcado</span>
                  </div>
                </td>
                <td className="px-6 py-5">
                   <div className="flex flex-col">
                    <span className="text-sm font-bold text-gray-700 dark:text-gray-300">
                      {formatAmount(order.entry_amount)}
                    </span>
                    <span className="text-[10px] text-gray-400 uppercase font-medium">{order.symbol.split('/')[0]}</span>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <StatusBadge status="ACTIVE" />
                </td>
                <td className="px-6 py-5 text-right">
                   <div className="flex flex-col items-end gap-1">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300">
                      <Clock className="w-3 h-3 text-gray-400" />
                      {format(new Date(order.entry_datetime), 'HH:mm:ss')}
                    </div>
                    <span className="text-[10px] text-gray-400 font-medium">
                      {format(new Date(order.entry_datetime), 'dd MMM yyyy')}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="p-4 bg-gray-50/50 dark:bg-gray-900/20 border-t border-gray-100 dark:border-gray-700/50 flex justify-end">
        <div className="flex items-center gap-2 text-[10px] font-bold text-indigo-400/70 uppercase tracking-widest leading-none">
          <ShieldCheck className="w-3 h-3" />
          Datos en tiempo real desde Binance algo-service
        </div>
      </div>
    </div>
  )
}
