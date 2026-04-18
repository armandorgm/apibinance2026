'use client'

/**
 * AtomicLifoView — Vista "Stack / Último en Entrar"
 *
 * Filosofía: LIFO implica que el trade más reciente se cierra primero.
 * Visualizamos la "pila" de posiciones con profundidad Z y numeración de nivel.
 * Las más recientes están al frente (más opacas/saturadas).
 */

import React, { useState } from 'react'
import { Trade } from '@/lib/api'
import { formatPrice, formatAmount } from '@/lib/utils'
import { OriginatorBadge, OrderIdBadge, TypeTagBadges, FillsSubTable, PnlBadge, formatDuration, formatDateTime, ExpandToggle } from './shared'
import { Layers, Clock, TrendingUp, TrendingDown } from 'lucide-react'

interface Props {
  trades: Trade[]
}

const LEVEL_COLORS = [
  { border: 'border-violet-500', bg: 'bg-violet-50 dark:bg-violet-900/20', opacity: '1', shadow: 'shadow-violet-200/50 dark:shadow-violet-900/30' },
  { border: 'border-violet-400', bg: 'bg-violet-50/80 dark:bg-violet-900/15', opacity: '0.9', shadow: 'shadow-violet-100/50 dark:shadow-violet-900/20' },
  { border: 'border-violet-300', bg: 'bg-violet-50/60 dark:bg-violet-900/10', opacity: '0.8', shadow: '' },
  { border: 'border-slate-300 dark:border-slate-600', bg: 'bg-white dark:bg-gray-900', opacity: '0.65', shadow: '' },
]

function StackCard({ trade, level, isTop }: { trade: Trade; level: number; isTop: boolean }) {
  const [expanded, setExpanded] = useState(false)
  const hasFills = (trade.entry_fills?.length ?? 0) > 0 || (trade.exit_fills?.length ?? 0) > 0
  const positive = trade.pnl_net >= 0
  const color = LEVEL_COLORS[Math.min(level, LEVEL_COLORS.length - 1)]

  return (
    <div
      className={`
        relative rounded-xl border-2 transition-all duration-300 overflow-hidden
        ${color.border} ${color.bg}
        ${isTop ? 'shadow-xl ' + color.shadow : 'shadow-sm'}
        ${positive ? '' : 'border-l-4 border-l-rose-500'}
        hover:shadow-lg hover:-translate-y-0.5
      `}
    >
      {/* Level badge */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5">
        <span className={`
          flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold
          ${isTop
            ? 'bg-violet-600 text-white'
            : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
          }
        `}>
          <Layers className="w-3 h-3" />
          #{level + 1}
          {isTop && <span className="ml-1 opacity-80">top</span>}
        </span>
      </div>

      <div className="p-4 pr-20">
        {/* Header */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-bold text-gray-800 dark:text-white uppercase tracking-wide">{trade.symbol}</span>
          <OriginatorBadge originator={trade.originator} />
          <span className="text-[10px] text-slate-400">{formatDateTime(trade.entry_datetime)}</span>
        </div>

        {/* Main metrics grid */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {/* Entry */}
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Entrada</span>
            <span className="text-base font-bold text-gray-900 dark:text-white tabular-nums">{formatPrice(trade.entry_price)}</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">{formatAmount(trade.entry_amount)}</span>
            <OrderIdBadge id={trade.entry_order_id} />
          </div>

          {/* Exit */}
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Salida</span>
            {trade.exit_price ? (
              <>
                <span className="text-base font-bold text-gray-900 dark:text-white tabular-nums">{formatPrice(trade.exit_price)}</span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">{formatAmount(trade.exit_amount ?? 0)}</span>
                <OrderIdBadge id={trade.exit_order_id} />
              </>
            ) : (
              <span className="flex items-center gap-1 text-xs italic text-gray-400 dark:text-gray-500 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50 animate-pulse inline-block" />
                Abierta
              </span>
            )}
          </div>

          {/* Duration */}
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Duración</span>
            {trade.duration_seconds > 0 ? (
              <span className="flex items-center gap-1 text-sm font-bold text-gray-700 dark:text-gray-300">
                <Clock className="w-3.5 h-3.5 text-violet-500" />
                {formatDuration(trade.duration_seconds)}
              </span>
            ) : (
              <span className="text-xs text-slate-400 italic">—</span>
            )}
            <span className="text-[10px] text-slate-400">Fee: {formatAmount(trade.entry_fee + (trade.exit_fee ?? 0))}</span>
          </div>

          {/* PnL */}
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1">
              {positive ? <TrendingUp className="w-3 h-3 text-emerald-500" /> : <TrendingDown className="w-3 h-3 text-rose-500" />}
              Resultado
            </span>
            <PnlBadge pnl={trade.pnl_net} percentage={trade.pnl_percentage} />
          </div>
        </div>

        {/* Tags */}
        <div className="flex items-center gap-2 mt-3">
          <TypeTagBadges tags={trade.entry_order_tags} variant="entry" />
          {trade.exit_order_tags && trade.exit_order_tags.length > 0 && (
            <TypeTagBadges tags={trade.exit_order_tags} variant="exit" />
          )}
          <ExpandToggle expanded={expanded} onToggle={() => setExpanded(!expanded)} hasFills={hasFills} />
        </div>
      </div>

      {/* Expandable fills */}
      {expanded && hasFills && (
        <div className="px-4 pb-3 border-t border-slate-100/60 dark:border-slate-800/40 bg-white/50 dark:bg-black/10">
          <FillsSubTable fills={trade.entry_fills} title="Entrada" />
          <FillsSubTable fills={trade.exit_fills} title="Salida" />
        </div>
      )}

      {/* Bottom accent bar */}
      <div
        className={`h-1 w-full ${positive ? 'bg-gradient-to-r from-emerald-400 to-emerald-600' : 'bg-gradient-to-r from-rose-400 to-rose-600'}`}
        style={{ opacity: isTop ? 1 : 0.4 }}
      />
    </div>
  )
}

export function AtomicLifoView({ trades }: Props) {
  if (trades.length === 0) {
    return (
      <div className="p-12 text-center text-gray-400 dark:text-gray-500">
        <div className="text-4xl mb-3">📚</div>
        <p className="text-sm">No hay posiciones emparejadas con Atomic LIFO.</p>
      </div>
    )
  }

  const totalPnl = trades.reduce((acc, t) => acc + t.pnl_net, 0)
  const wins = trades.filter((t) => t.pnl_net >= 0).length

  return (
    <div className="p-6 flex flex-col gap-4">
      {/* Stack summary header */}
      <div className="flex items-center gap-4 p-3 rounded-xl bg-violet-50 dark:bg-violet-900/20 border border-violet-200/50 dark:border-violet-800/40">
        <Layers className="w-5 h-5 text-violet-500 flex-shrink-0" />
        <div className="flex gap-6 text-sm flex-wrap">
          <span className="text-slate-600 dark:text-slate-300">
            <span className="font-bold text-violet-700 dark:text-violet-300">{trades.length}</span> posiciones en pila
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            PnL acumulado:{' '}
            <span className={`font-bold ${totalPnl >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
              {totalPnl >= 0 ? '+' : ''}{formatPrice(totalPnl)}
            </span>
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            Win rate: <span className="font-bold text-violet-700 dark:text-violet-300">{((wins / trades.length) * 100).toFixed(0)}%</span>
          </span>
        </div>
        <div className="ml-auto text-[10px] text-violet-500 font-semibold uppercase tracking-wider">
          🕐 El #1 fue cerrado primero
        </div>
      </div>

      {/* Legend */}
      <div className="text-[10px] text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
        Vista Stack (LIFO) — el trade más reciente al frente (#1). Borde izquierdo rojo = pérdida.
      </div>

      {/* Stack cards — #1 = most recently closed (top of LIFO stack) */}
      <div className="flex flex-col gap-3">
        {trades.map((trade, i) => (
          <StackCard key={trade.id} trade={trade} level={i} isTop={i === 0} />
        ))}
      </div>
    </div>
  )
}
