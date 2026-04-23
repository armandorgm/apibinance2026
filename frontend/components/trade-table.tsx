'use client'

import React, { useState } from 'react'
import { Trade, FillDetail } from '@/lib/api'
import { format } from 'date-fns'
import { formatPrice, formatAmount, formatPercentage } from '@/lib/utils'
import { ChevronDown, ChevronRight, ListTree, Zap, ShieldCheck, History } from 'lucide-react'

interface TradeTableProps {
  trades: Trade[]
}

function OriginatorBadge({ originator }: { originator: string | undefined }) {
  if (!originator) return null;
  
  const config: Record<string, { label: string; icon: string; className: string }> = {
    'BOT_APP': { label: 'BOT', icon: '🤖', className: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300' },
    'MANUAL': { label: 'MANUAL', icon: '👤', className: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' },
    'AUTO_ALGO': { label: 'AUTO', icon: '⚡', className: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300' },
  };

  const { label, icon, className } = config[originator] || { label: originator, icon: '❓', className: 'bg-gray-100 text-gray-700 dark:bg-gray-800' };

  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight ${className}`}>
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

function OrderIdBadge({ id }: { id: string | null | undefined }) {
  if (!id || id === '') return null;
  return (
    <span className="inline-flex items-center font-mono text-[9px] text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-900/50 px-1 rounded border border-gray-100 dark:border-gray-800" title={`Binance Order ID: ${id}`}>
      #{id}
    </span>
  );
}

function TypeTagBadges({ tags, variant }: { tags: string[] | undefined; variant: 'entry' | 'exit' }) {
  const list = tags && tags.length > 0 ? tags : []
  const base =
    variant === 'entry'
      ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200 border border-emerald-200/60 dark:border-emerald-800/60'
      : 'bg-amber-50 text-amber-900 dark:bg-amber-900/25 dark:text-amber-100 border border-amber-200/60 dark:border-amber-800/60'

  if (list.length === 0) {
    return (
      <span className="text-[10px] text-gray-400 dark:text-gray-500 mt-1" title="Sin tipo en datos; sincroniza o espera enriquecimiento">
        —
      </span>
    )
  }

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {list.map((tag) => (
        <span
          key={tag}
          className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${base}`}
        >
          {tag}
        </span>
      ))}
    </div>
  )
}

function FillsSubTable({ fills, title }: { fills: FillDetail[] | undefined; title: string }) {
  if (!fills || fills.length === 0) return null;

  return (
    <div className="mt-2 mb-4 overflow-hidden rounded-lg border border-slate-100 dark:border-slate-800/60 shadow-sm">
      <div className="bg-slate-50/50 dark:bg-slate-900/50 px-3 py-1.5 border-b border-slate-100 dark:border-slate-800/60 flex items-center gap-2">
        <History className="w-3 h-3 text-slate-400" />
        <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title} (Executions)</span>
      </div>
      <table className="w-full text-[11px]">
        <thead>
          <tr className="bg-white dark:bg-slate-950/20 text-slate-400 text-[9px] uppercase">
            <th className="px-3 py-1.5 text-left font-medium">Trade ID</th>
            <th className="px-3 py-1.5 text-left font-medium">Price</th>
            <th className="px-3 py-1.5 text-left font-medium">Quantity</th>
            <th className="px-3 py-1.5 text-left font-medium">Fee</th>
            <th className="px-3 py-1.5 text-left font-medium">Role</th>
            <th className="px-3 py-1.5 text-right font-medium">Time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800/40">
          {fills.map((fill) => (
            <tr key={fill.trade_id} className="hover:bg-slate-50/30 dark:hover:bg-slate-800/20 transition-colors">
              <td className="px-3 py-2 font-mono text-[10px] font-medium text-slate-500 dark:text-slate-400">
                #{fill.trade_id}
              </td>
              <td className="px-3 py-2 text-slate-700 dark:text-slate-300 font-semibold">{formatPrice(fill.price)}</td>
              <td className="px-3 py-2 text-slate-600 dark:text-slate-400">{formatAmount(fill.amount)}</td>
              <td className="px-3 py-2 text-rose-500/80 dark:text-rose-400/80">-{formatAmount(fill.fee)}</td>
              <td className="px-3 py-2">
                <span className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[9px] font-bold text-slate-500 uppercase">
                  {fill.role}
                </span>
              </td>
              <td className="px-3 py-2 text-right text-slate-400">
                {fill.datetime.split('T')[1].split('.')[0]}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function TradeTable({ trades }: TradeTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

  if (trades.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 dark:text-gray-400">
        No hay operaciones registradas. Haz clic en "Sincronizar" para obtener tus trades de Binance.
      </div>
    )
  }

  const toggleRow = (id: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedRows(newExpanded)
  }

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm:ss')
  }

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th className="w-8 px-4 py-3"></th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Entrada
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Salida
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Métricas
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Resultado
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-slate-950 divide-y divide-gray-100 dark:divide-gray-800">
          {trades.map((trade) => {
            const isExpanded = expandedRows.has(trade.id)
            const hasFills = (trade.entry_fills?.length || 0) > 0 || (trade.exit_fills?.length || 0) > 0

            return (
              <React.Fragment key={trade.id}>
                <tr 
                  className={`group hover:bg-gray-50/50 dark:hover:bg-gray-900/30 transition-colors cursor-pointer ${isExpanded ? 'bg-indigo-50/10 dark:bg-indigo-900/5' : ''}`}
                  onClick={() => toggleRow(trade.id)}
                >
                  <td className="px-4 py-4 text-center">
                    {hasFills && (
                      isExpanded ? <ChevronDown className="w-4 h-4 text-indigo-500" /> : <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                  </td>
                  
                  {/* Entrada */}
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-gray-900 dark:text-white uppercase">
                          {trade.symbol}
                        </span>
                        <OriginatorBadge originator={trade.originator} />
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400 uppercase">
                          {trade.entry_side}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          @ {formatPrice(trade.entry_price)}
                        </span>
                      </div>
                      <div className="text-[10px] text-gray-400 dark:text-gray-500 mt-1">
                        {formatDate(trade.entry_datetime)}
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <OrderIdBadge id={trade.entry_order_id} />
                        <TypeTagBadges tags={trade.entry_order_tags} variant="entry" />
                      </div>
                    </div>
                  </td>

                  {/* Salida */}
                  <td className="px-6 py-4">
                    {trade.exit_side ? (
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs font-medium text-amber-600 dark:text-amber-400 uppercase">
                            {trade.exit_side}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            @ {formatPrice(trade.exit_price || 0)}
                          </span>
                        </div>
                        <div className="text-[10px] text-gray-400 dark:text-gray-500 mt-1">
                          {formatDate(trade.exit_datetime || '')}
                        </div>
                        <div className="mt-1 flex items-center gap-2">
                          <OrderIdBadge id={trade.exit_order_id} />
                          <TypeTagBadges tags={trade.exit_order_tags} variant="exit" />
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs italic text-gray-400 dark:text-gray-500 flex items-center gap-2">
                         <span className="inline-block w-2 h-2 rounded-full bg-emerald-500/50 animate-pulse" />
                         Abierto / Parcial
                      </div>
                    )}
                  </td>

                  {/* Métricas */}
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {formatAmount(trade.entry_amount)}
                      </div>
                      <div className="text-xs text-gray-400 dark:text-gray-500">
                        Fee: {formatAmount(trade.entry_fee + (trade.exit_fee || 0))} 
                      </div>
                      {trade.duration_seconds > 0 && (
                        <div className="text-[10px] text-gray-400 dark:text-gray-500 mt-1 bg-gray-50 dark:bg-gray-900 px-1 py-0.5 rounded w-fit">
                          Duración: {formatDuration(trade.duration_seconds)}
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Resultado (PnL) */}
                  <td className="px-6 py-4 text-right">
                    <div className="flex flex-col items-end">
                      <div className={`text-sm font-bold ${trade.pnl_net >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                        {trade.pnl_net >= 0 ? '+' : ''}{formatPrice(trade.pnl_net)}
                      </div>
                      <div className={`text-xs font-semibold px-1 rounded ${trade.pnl_percentage >= 0 ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30' : 'bg-rose-50 text-rose-600 dark:bg-rose-900/30'}`}>
                        {trade.pnl_percentage >= 0 ? '+' : ''}{formatPercentage(trade.pnl_percentage)}
                      </div>
                    </div>
                  </td>
                </tr>

                {/* Detalle Expandible (Total Transparency) */}
                {isExpanded && hasFills && (
                  <tr className="bg-slate-50/30 dark:bg-slate-900/20">
                    <td colSpan={5} className="px-12 py-2">
                      <div className="flex flex-col gap-2">
                        <FillsSubTable fills={trade.entry_fills} title="Entrada" />
                        <FillsSubTable fills={trade.exit_fills} title="Salida" />
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
