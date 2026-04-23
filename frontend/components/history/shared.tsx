'use client'

import React, { useState } from 'react'
import { FillDetail } from '@/lib/api'
import { formatPrice, formatAmount } from '@/lib/utils'
import { History, ChevronDown, ChevronRight } from 'lucide-react'

// ─────────────────────────────────────────────
// OriginatorBadge
// ─────────────────────────────────────────────
export function OriginatorBadge({ originator }: { originator: string | undefined }) {
  if (!originator) return null
  const config: Record<string, { label: string; icon: string; className: string }> = {
    BOT_APP: { label: 'BOT', icon: '🤖', className: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300' },
    MANUAL:  { label: 'MANUAL', icon: '👤', className: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' },
    AUTO_ALGO: { label: 'AUTO', icon: '⚡', className: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300' },
  }
  const { label, icon, className } = config[originator] ?? { label: originator, icon: '❓', className: 'bg-gray-100 text-gray-700 dark:bg-gray-800' }
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight ${className}`}>
      <span>{icon}</span><span>{label}</span>
    </span>
  )
}

// ─────────────────────────────────────────────
// OrderIdBadge
// ─────────────────────────────────────────────
export function OrderIdBadge({ id }: { id: string | null | undefined }) {
  if (!id || id === '') return null
  return (
    <span
      className="inline-flex items-center font-mono text-[9px] text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-900/50 px-1 rounded border border-gray-100 dark:border-gray-800"
      title={`Binance Order ID: ${id}`}
    >
      #{id}
    </span>
  )
}

// ─────────────────────────────────────────────
// TypeTagBadges
// ─────────────────────────────────────────────
export function TypeTagBadges({ tags, variant }: { tags: string[] | undefined; variant: 'entry' | 'exit' }) {
  const list = tags && tags.length > 0 ? tags : []
  const base =
    variant === 'entry'
      ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200 border border-emerald-200/60 dark:border-emerald-800/60'
      : 'bg-amber-50 text-amber-900 dark:bg-amber-900/25 dark:text-amber-100 border border-amber-200/60 dark:border-amber-800/60'
  if (list.length === 0) return <span className="text-[10px] text-gray-400 dark:text-gray-500">—</span>
  return (
    <div className="flex flex-wrap gap-1">
      {list.map((tag) => (
        <span key={tag} className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${base}`}>{tag}</span>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────
// FillsSubTable
// ─────────────────────────────────────────────
export function FillsSubTable({ fills, title }: { fills: FillDetail[] | undefined; title: string }) {
  if (!fills || fills.length === 0) return null
  return (
    <div className="mt-2 mb-3 overflow-hidden rounded-lg border border-slate-100 dark:border-slate-800/60 shadow-sm">
      <div className="bg-slate-50/50 dark:bg-slate-900/50 px-3 py-1.5 border-b border-slate-100 dark:border-slate-800/60 flex items-center gap-2">
        <History className="w-3 h-3 text-slate-400" />
        <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title} (Executions)</span>
      </div>
      <table className="w-full text-[11px]">
        <thead>
          <tr className="bg-white dark:bg-slate-950/20 text-slate-400 text-[9px] uppercase">
            <th className="px-3 py-1.5 text-left font-medium">Trade ID</th>
            <th className="px-3 py-1.5 text-left font-medium">Price</th>
            <th className="px-3 py-1.5 text-left font-medium">Qty</th>
            <th className="px-3 py-1.5 text-left font-medium">Fee</th>
            <th className="px-3 py-1.5 text-right font-medium">Time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800/40">
          {fills.map((fill) => (
            <tr key={fill.trade_id} className="hover:bg-slate-50/30 dark:hover:bg-slate-800/20 transition-colors">
              <td className="px-3 py-1.5 font-mono text-[10px] text-slate-500 dark:text-slate-400">#{fill.trade_id}</td>
              <td className="px-3 py-1.5 text-slate-700 dark:text-slate-300 font-semibold">{formatPrice(fill.price)}</td>
              <td className="px-3 py-1.5 text-slate-600 dark:text-slate-400">{formatAmount(fill.amount)}</td>
              <td className="px-3 py-1.5 text-rose-500/80 dark:text-rose-400/80">-{formatAmount(fill.fee)}</td>
              <td className="px-3 py-1.5 text-right text-slate-400">{fill.datetime.split('T')[1]?.split('.')[0] ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─────────────────────────────────────────────
// ExpandToggle — generic expand/collapse wrapper
// ─────────────────────────────────────────────
export function ExpandToggle({ expanded, onToggle, hasFills }: { expanded: boolean; onToggle: () => void; hasFills: boolean }) {
  if (!hasFills) return null
  return (
    <button
      onClick={onToggle}
      className="flex items-center gap-1 text-[10px] text-indigo-500 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors mt-2"
    >
      {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      {expanded ? 'Ocultar executions' : 'Ver executions'}
    </button>
  )
}

// ─────────────────────────────────────────────
// PnL helpers
// ─────────────────────────────────────────────
export function PnlBadge({ pnl, percentage }: { pnl: number; percentage: number }) {
  const positive = pnl >= 0
  return (
    <div className="flex flex-col items-end gap-0.5">
      <span className={`text-sm font-bold tabular-nums ${positive ? 'text-emerald-500' : 'text-rose-500'}`}>
        {positive ? '+' : ''}{formatPrice(pnl)}
      </span>
      <span className={`text-[11px] font-semibold px-1.5 py-0.5 rounded ${positive ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300' : 'bg-rose-50 text-rose-600 dark:bg-rose-900/30 dark:text-rose-300'}`}>
        {positive ? '+' : ''}{percentage.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%
      </span>
    </div>
  )
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}h ${m}m`
}

export function formatDateTime(dateString: string): string {
  try {
    const d = new Date(dateString)
    return d.toLocaleString('es-AR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch { return dateString }
}
