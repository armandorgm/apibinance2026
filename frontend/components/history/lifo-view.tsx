'use client'

/**
 * LifoView — Vista "Timeline / Profundidad de Mercado"
 *
 * Filosofía: LIFO con parciales es la forma más agresiva — los trades más recientes
 * salen primero. Útil para scalpers. Muestra compras y ventas como eventos
 * separados en una línea de tiempo mixta con flechas de emparejamiento.
 */

import React, { useState } from 'react'
import { Trade } from '@/lib/api'
import { formatPrice, formatAmount } from '@/lib/utils'
import { OriginatorBadge, FillsSubTable, PnlBadge, formatDuration, formatDateTime, ExpandToggle } from './shared'
import { Zap, ArrowDown, ChevronRight } from 'lucide-react'

interface Props {
  trades: Trade[]
}

/** Build a unified event list from matched trades for timeline rendering */
interface TimelineEvent {
  id: string
  tradeId: number
  type: 'buy' | 'sell' | 'pair'
  side: string
  price: number
  amount: number
  datetime: string
  pnl?: number
  pnlPct?: number
  duration?: number
  originator?: string
  partialOf?: string        // links sell back to its buy match
  buyPrice?: number         // for sell events, show the matched buy price
  entry_fills?: Trade['entry_fills']
  exit_fills?: Trade['exit_fills']
}

function buildTimeline(trades: Trade[]): TimelineEvent[] {
  const events: TimelineEvent[] = []

  for (const t of trades) {
    // Each matched trade → one "pair" event displayed as a mini summary row
    events.push({
      id: `pair-${t.id}`,
      tradeId: t.id,
      type: 'pair',
      side: t.entry_side,
      price: t.entry_price,
      amount: t.entry_amount,
      datetime: t.entry_datetime,
      pnl: t.pnl_net,
      pnlPct: t.pnl_percentage,
      duration: t.duration_seconds,
      originator: t.originator,
      buyPrice: t.entry_price,
      entry_fills: t.entry_fills,
      exit_fills: t.exit_fills,
    })
  }

  // Sort by datetime descending (most recent first — LIFO spirit)
  return events.sort((a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime())
}

function TimelineRow({ event, trade, isLast }: { event: TimelineEvent; trade: Trade; isLast: boolean }) {
  const [expanded, setExpanded] = useState(false)
  const hasFills = (trade.entry_fills?.length ?? 0) > 0 || (trade.exit_fills?.length ?? 0) > 0
  const positive = (event.pnl ?? 0) >= 0

  return (
    <div className="flex gap-0">
      {/* Timeline spine */}
      <div className="flex flex-col items-center w-10 flex-shrink-0">
        {/* Dot */}
        <div className={`
          w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 z-10 mt-4
          ${positive
            ? 'bg-emerald-500 shadow-emerald-500/40 shadow-md'
            : 'bg-rose-500 shadow-rose-500/40 shadow-md'
          }
        `}>
          {positive
            ? <span className="text-[8px] text-white font-bold">▲</span>
            : <span className="text-[8px] text-white font-bold">▼</span>
          }
        </div>
        {/* Line */}
        {!isLast && <div className="w-0.5 flex-1 bg-slate-200 dark:bg-slate-700 mt-1" />}
      </div>

      {/* Event card */}
      <div className={`
        flex-1 mb-3 rounded-xl border transition-all duration-200 overflow-hidden
        ${positive
          ? 'border-emerald-200/60 dark:border-emerald-800/40 hover:border-emerald-400/60'
          : 'border-rose-200/60 dark:border-rose-800/40 hover:border-rose-400/60'
        }
        bg-white dark:bg-gray-900 shadow-sm hover:shadow-md
      `}>
        {/* Top color strip */}
        <div className={`h-1 ${positive ? 'bg-gradient-to-r from-emerald-400 to-teal-500' : 'bg-gradient-to-r from-rose-400 to-pink-500'}`} />

        <div className="p-4">
          {/* Header row */}
          <div className="flex items-start justify-between gap-3">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <OriginatorBadge originator={event.originator} />
                <span className="text-[10px] font-bold uppercase tracking-widest text-amber-600 dark:text-amber-400">
                  LIFO Match
                </span>
                <span className="text-[10px] text-slate-400">{formatDateTime(event.datetime)}</span>
              </div>

              {/* Buy → Sell arrow chain */}
              <div className="flex items-center gap-2 mt-1">
                {/* BUY side */}
                <div className="flex items-center gap-1.5 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200/60 dark:border-emerald-800/40 rounded-lg px-3 py-1.5">
                  <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-300 uppercase">BUY</span>
                  <span className="text-sm font-bold text-gray-900 dark:text-white tabular-nums">{formatPrice(trade.entry_price)}</span>
                  <span className="text-[11px] text-slate-500 dark:text-slate-400">× {formatAmount(trade.entry_amount)}</span>
                </div>

                {/* Chain arrow */}
                <div className="flex flex-col items-center">
                  <ChevronRight className="w-4 h-4 text-amber-500" />
                  {event.duration != null && event.duration > 0 && (
                    <span className="text-[8px] text-amber-500 font-semibold">{formatDuration(event.duration)}</span>
                  )}
                </div>

                {/* SELL side */}
                {trade.exit_price ? (
                  <div className="flex items-center gap-1.5 bg-amber-50 dark:bg-amber-900/20 border border-amber-200/60 dark:border-amber-800/40 rounded-lg px-3 py-1.5">
                    <span className="text-[10px] font-bold text-amber-700 dark:text-amber-300 uppercase">SELL</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white tabular-nums">{formatPrice(trade.exit_price)}</span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400">× {formatAmount(trade.exit_amount ?? 0)}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50 animate-pulse inline-block" />
                    <span className="text-[10px] italic text-slate-400">Posición abierta</span>
                  </div>
                )}
              </div>
            </div>

            {/* PnL */}
            {event.pnl != null && event.pnlPct != null && (
              <div className="flex-shrink-0">
                <PnlBadge pnl={event.pnl} percentage={event.pnlPct} />
              </div>
            )}
          </div>

          {/* Bottom: symbol, fee, expand */}
          <div className="flex items-center gap-4 mt-2 text-[10px] text-slate-400 dark:text-slate-500">
            <span className="font-bold text-slate-600 dark:text-slate-300 uppercase">{trade.symbol}</span>
            <span>Fee entrada: <span className="text-rose-400">-{formatAmount(trade.entry_fee)}</span></span>
            {trade.exit_fee != null && (
              <span>Fee salida: <span className="text-rose-400">-{formatAmount(trade.exit_fee)}</span></span>
            )}
            <ExpandToggle expanded={expanded} onToggle={() => setExpanded(!expanded)} hasFills={hasFills} />
          </div>
        </div>

        {/* Expandable fills */}
        {expanded && hasFills && (
          <div className="px-4 pb-3 border-t border-slate-100 dark:border-slate-800/50 bg-slate-50/30 dark:bg-slate-900/30">
            <FillsSubTable fills={trade.entry_fills} title="Entrada" />
            <FillsSubTable fills={trade.exit_fills} title="Salida" />
          </div>
        )}
      </div>
    </div>
  )
}

export function LifoView({ trades }: Props) {
  if (trades.length === 0) {
    return (
      <div className="p-12 text-center text-gray-400 dark:text-gray-500">
        <div className="text-4xl mb-3">⚡</div>
        <p className="text-sm">No hay posiciones emparejadas con LIFO Puro.</p>
      </div>
    )
  }

  // Sort trades descending by entry datetime (LIFO spirit — most recent at top)
  const sorted = [...trades].sort(
    (a, b) => new Date(b.entry_datetime).getTime() - new Date(a.entry_datetime).getTime()
  )

  const totalPnl = trades.reduce((acc, t) => acc + t.pnl_net, 0)
  const wins = trades.filter((t) => t.pnl_net >= 0).length
  const totalTrades = trades.length

  // Average duration
  const avgDuration = trades.reduce((acc, t) => acc + t.duration_seconds, 0) / totalTrades

  const events = buildTimeline(trades)

  return (
    <div className="p-6 flex flex-col gap-4">
      {/* Scalper summary header */}
      <div className="flex items-center gap-4 p-3 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200/50 dark:border-amber-800/40">
        <Zap className="w-5 h-5 text-amber-500 flex-shrink-0" />
        <div className="flex gap-5 text-sm flex-wrap">
          <span className="text-slate-600 dark:text-slate-300">
            <span className="font-bold text-amber-700 dark:text-amber-300">{totalTrades}</span> operaciones
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            PnL total:{' '}
            <span className={`font-bold ${totalPnl >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {totalPnl >= 0 ? '+' : ''}{formatPrice(totalPnl)}
            </span>
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            Win rate: <span className="font-bold text-amber-700 dark:text-amber-300">{((wins / totalTrades) * 100).toFixed(0)}%</span>
          </span>
          {avgDuration > 0 && (
            <span className="text-slate-600 dark:text-slate-300">
              Duración promedio: <span className="font-bold text-amber-700 dark:text-amber-300">{formatDuration(Math.round(avgDuration))}</span>
            </span>
          )}
        </div>
        <div className="ml-auto text-[10px] text-amber-500 font-semibold uppercase tracking-wider">
          ⚡ Más reciente primero
        </div>
      </div>

      {/* Legend */}
      <div className="text-[10px] text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
        Vista Timeline (LIFO Puro) — cada evento muestra el par BUY→SELL, más reciente primero.
        Verde = ganancia ▲ / Rojo = pérdida ▼
      </div>

      {/* Timeline */}
      <div className="flex flex-col pl-2">
        {sorted.map((trade, i) => {
          const event = events.find((e) => e.tradeId === trade.id)
          if (!event) return null
          return (
            <TimelineRow
              key={trade.id}
              event={event}
              trade={trade}
              isLast={i === sorted.length - 1}
            />
          )
        })}
      </div>
    </div>
  )
}
