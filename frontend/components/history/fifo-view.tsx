'use client'

/**
 * FifoView — Vista "Ledger / Inventario Contable"
 *
 * Filosofía: FIFO con parciales sigue el principio contable de gestión de inventario.
 * Muestra lotes de compra con barra de consumo y las ventas que los consumieron.
 * Layout tipo libro mayor en dos paneles.
 */

import React, { useState } from 'react'
import { Trade } from '@/lib/api'
import { formatPrice, formatAmount } from '@/lib/utils'
import { OriginatorBadge, OrderIdBadge, TypeTagBadges, FillsSubTable, PnlBadge, formatDuration, formatDateTime, ExpandToggle } from './shared'
import { BookOpen, ArrowRight, Package } from 'lucide-react'

interface Props {
  trades: Trade[]
}

/**
 * Groups sequential trades that share the same entry_order_id (same buy lot).
 * If no grouping is possible, each trade is its own group.
 */
function groupByEntryLot(trades: Trade[]): Array<{ lotId: string; buyPrice: number; totalBuyAmount: number; sellTrades: Trade[] }> {
  const groups: Map<string, { lotId: string; buyPrice: number; totalBuyAmount: number; sellTrades: Trade[] }> = new Map()

  for (const t of trades) {
    const key = t.entry_order_id ?? `trade_${t.id}`
    if (!groups.has(key)) {
      groups.set(key, {
        lotId: key,
        buyPrice: t.entry_price,
        totalBuyAmount: t.entry_amount,
        sellTrades: [],
      })
    }
    const g = groups.get(key)!
    g.sellTrades.push(t)
    // Track total consumed amount per lot
    if (g.sellTrades.length > 1) {
      g.totalBuyAmount = g.sellTrades.reduce((acc, st) => acc + st.entry_amount, 0)
    }
  }

  return Array.from(groups.values())
}

function LotRow({ group, lotIndex }: { group: ReturnType<typeof groupByEntryLot>[0]; lotIndex: number }) {
  const [expandedTrade, setExpandedTrade] = useState<number | null>(null)

  const totalConsumed = group.sellTrades.reduce((acc, t) => acc + (t.exit_amount ?? 0), 0)
  const consumePct = group.totalBuyAmount > 0 ? Math.min((totalConsumed / group.totalBuyAmount) * 100, 100) : 0
  const lotPnl = group.sellTrades.reduce((acc, t) => acc + t.pnl_net, 0)
  const lotPnlPositive = lotPnl >= 0
  const isFullyConsumed = consumePct >= 99.9

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden bg-white dark:bg-gray-900 shadow-sm hover:shadow-md transition-shadow">
      {/* Lot header */}
      <div className="flex items-center gap-4 px-5 py-3 bg-emerald-50/80 dark:bg-emerald-900/10 border-b border-emerald-200/50 dark:border-emerald-800/30">
        <div className="flex items-center gap-2">
          <Package className="w-4 h-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
          <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-700 dark:text-emerald-300">
            Lote #{lotIndex + 1}
          </span>
        </div>
        <OrderIdBadge id={group.lotId.startsWith('trade_') ? null : group.lotId} />
        <span className="text-sm font-bold text-gray-900 dark:text-white">{formatPrice(group.buyPrice)}</span>
        <span className="text-xs text-slate-500 dark:text-slate-400">× {formatAmount(group.totalBuyAmount)}</span>
        <div className="ml-auto flex items-center gap-3">
          <span className={`text-xs font-bold ${lotPnlPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
            {lotPnlPositive ? '+' : ''}{formatPrice(lotPnl)}
          </span>
          {isFullyConsumed && (
            <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
              Consumido
            </span>
          )}
        </div>
      </div>

      {/* Consumption progress bar */}
      <div className="px-5 py-2 border-b border-slate-100 dark:border-slate-800/50 flex items-center gap-3">
        <span className="text-[10px] text-slate-500 dark:text-slate-400 w-20 flex-shrink-0">Consumo</span>
        <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${isFullyConsumed ? 'bg-slate-400 dark:bg-slate-600' : 'bg-emerald-500 dark:bg-emerald-400'}`}
            style={{ width: `${consumePct}%` }}
          />
        </div>
        <span className="text-[10px] font-bold text-slate-600 dark:text-slate-300 w-12 text-right">{consumePct.toFixed(0)}%</span>
        <span className="text-[10px] text-slate-400 dark:text-slate-500">
          {formatAmount(totalConsumed)} / {formatAmount(group.totalBuyAmount)}
        </span>
      </div>

      {/* Sell trades within this lot */}
      <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
        {group.sellTrades.map((trade, si) => {
          const isExpanded = expandedTrade === trade.id
          const hasFills = (trade.entry_fills?.length ?? 0) > 0 || (trade.exit_fills?.length ?? 0) > 0

          return (
            <div key={trade.id} className="px-5 py-3">
              <div className="flex items-start gap-4">
                {/* Sale index + arrow */}
                <div className="flex items-center gap-2 flex-shrink-0 mt-0.5">
                  <div className="w-5 h-5 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-[9px] font-bold text-amber-700 dark:text-amber-300">
                    {si + 1}
                  </div>
                  <ArrowRight className="w-3 h-3 text-slate-300 dark:text-slate-600" />
                </div>

                {/* Sale details */}
                <div className="flex-1 flex items-center gap-4 flex-wrap">
                  <div className="flex flex-col gap-0.5 min-w-[100px]">
                    <span className="text-[10px] font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Venta</span>
                    <span className="text-sm font-bold text-gray-800 dark:text-gray-200 tabular-nums">
                      {formatPrice(trade.exit_price ?? 0)}
                    </span>
                    <span className="text-[11px] text-slate-500">{formatAmount(trade.exit_amount ?? 0)}</span>
                  </div>

                  {/* Spread */}
                  <div className="flex flex-col gap-0.5 min-w-[80px]">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider">Spread</span>
                    <span className={`text-sm font-bold tabular-nums ${(trade.exit_price ?? 0) >= trade.entry_price ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                      {(trade.exit_price ?? 0) >= trade.entry_price ? '+' : ''}{formatPrice((trade.exit_price ?? 0) - trade.entry_price)}
                    </span>
                  </div>

                  {/* Duration */}
                  {trade.duration_seconds > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider">Duración</span>
                      <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">{formatDuration(trade.duration_seconds)}</span>
                    </div>
                  )}

                  {/* Exit tags */}
                  <TypeTagBadges tags={trade.exit_order_tags} variant="exit" />

                  {/* Date */}
                  <span className="text-[10px] text-slate-400 ml-auto">{trade.exit_datetime ? formatDateTime(trade.exit_datetime) : '—'}</span>
                </div>

                {/* PnL */}
                <div className="flex-shrink-0">
                  <PnlBadge pnl={trade.pnl_net} percentage={trade.pnl_percentage} />
                </div>
              </div>

              {/* Expand link for fills */}
              {hasFills && (
                <div className="ml-9 mt-1">
                  <ExpandToggle expanded={isExpanded} onToggle={() => setExpandedTrade(isExpanded ? null : trade.id)} hasFills={hasFills} />
                  {isExpanded && (
                    <div className="mt-2">
                      <FillsSubTable fills={trade.entry_fills} title="Entrada" />
                      <FillsSubTable fills={trade.exit_fills} title="Salida" />
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function FifoView({ trades }: Props) {
  if (trades.length === 0) {
    return (
      <div className="p-12 text-center text-gray-400 dark:text-gray-500">
        <div className="text-4xl mb-3">📦</div>
        <p className="text-sm">No hay posiciones emparejadas con FIFO Puro.</p>
      </div>
    )
  }

  const groups = groupByEntryLot(trades)
  const totalPnl = trades.reduce((acc, t) => acc + t.pnl_net, 0)
  const totalFee = trades.reduce((acc, t) => acc + t.entry_fee + (t.exit_fee ?? 0), 0)

  // Weighted average buy price
  const totalCost = trades.reduce((acc, t) => acc + t.entry_price * t.entry_amount, 0)
  const totalAmount = trades.reduce((acc, t) => acc + t.entry_amount, 0)
  const avgBuyPrice = totalAmount > 0 ? totalCost / totalAmount : 0

  return (
    <div className="p-6 flex flex-col gap-4">
      {/* Ledger summary header */}
      <div className="flex items-center gap-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200/50 dark:border-emerald-800/40">
        <BookOpen className="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
        <div className="flex gap-6 text-sm flex-wrap">
          <span className="text-slate-600 dark:text-slate-300">
            <span className="font-bold text-emerald-700 dark:text-emerald-300">{groups.length}</span> lotes de compra
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            Precio promedio ponderado:{' '}
            <span className="font-bold text-emerald-700 dark:text-emerald-300">{formatPrice(avgBuyPrice)}</span>
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            PnL total:{' '}
            <span className={`font-bold ${totalPnl >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {totalPnl >= 0 ? '+' : ''}{formatPrice(totalPnl)}
            </span>
          </span>
          <span className="text-slate-600 dark:text-slate-300">
            Comisiones: <span className="font-bold text-rose-500">-{formatAmount(totalFee)}</span>
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="text-[10px] text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
        Vista Ledger (FIFO Puro) — cada fila verde es un lote de compra. Las ventas consumieron esos lotes en orden cronológico.
        La barra de progreso muestra qué % del lote fue liquidado.
      </div>

      {/* Lot groups */}
      <div className="flex flex-col gap-4">
        {groups.map((group, i) => (
          <LotRow key={group.lotId} group={group} lotIndex={i} />
        ))}
      </div>
    </div>
  )
}
