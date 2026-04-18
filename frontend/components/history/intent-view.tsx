'use client'

/**
 * IntentView — Monitor de Intención de Posición
 *
 * Filosofía: Cada Entrada se vincula a su Orden de Salida prevista cronológicamente
 * garantizando que "Take Profits" y "Limits" estén puramente mapeados a una intención original.
 * Las órdenes que no cumplen emparejamiento por no corresponder intencionalmente (o sobrar)
 * caen como "Huérfanas".
 */

import React, { useState } from 'react'
import { Trade, Order } from '@/lib/api'
import { formatPrice, formatAmount } from '@/lib/utils'
import { OriginatorBadge, OrderIdBadge, TypeTagBadges, FillsSubTable, PnlBadge, formatDuration, formatDateTime, ExpandToggle } from './shared'
import { ArrowRight, Clock } from 'lucide-react'

interface Props {
  trades: Trade[]
  symbol: string
}

function IntentCard({ trade, index }: { trade: Trade; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const hasFills = (trade.entry_fills?.length ?? 0) > 0 || (trade.exit_fills?.length ?? 0) > 0
  const positive = trade.pnl_net >= 0
  const pnlIntensity = Math.min(Math.abs(trade.pnl_percentage) / 5, 1) // normalize 0–5% → 0–1

  // Is the exit open (not filled)?
  const isExitOpen = !trade.exit_amount || trade.exit_amount === 0;

  // Determinar la naturaleza de la orden pendiente para el color del neón y labels
  const hasCond = (trade.exit_order_tags ?? []).includes('CONDITIONAL') || (trade.exit_order_tags ?? []).includes('ALGO') || (trade.exit_order_tags ?? []).includes('TAKE_PROFIT') || (trade.exit_order_tags ?? []).includes('STOP');
  const hasMarket = (trade.exit_order_tags ?? []).includes('MARKET');
  const isFloating = (trade.exit_order_tags ?? []).includes('FLOATING');

  let glowTheme = 'float';
  let neonColorClass = '';
  let neonBgClass = '';
  let neonTextColor = '';
  let statusText = 'Salida [FLOATING]';

  if (isExitOpen) {
    if (hasCond) {
      glowTheme = 'algo';
      neonColorClass = 'border-amber-400 dark:border-amber-500 animate-stepped-glow-algo';
      neonBgClass = 'bg-amber-50/10 dark:bg-amber-900/10';
      neonTextColor = 'text-amber-600 dark:text-amber-400';
      statusText = hasMarket ? 'Salida [ALGO / MARKET]' : 'Salida [ALGO / LIMIT]';
    } else if (!isFloating) {
      glowTheme = 'std';
      neonColorClass = 'border-sky-400 dark:border-sky-500 animate-stepped-glow-std';
      neonBgClass = 'bg-sky-50/10 dark:bg-sky-900/10';
      neonTextColor = 'text-sky-600 dark:text-sky-400';
      statusText = hasMarket ? 'Salida [STD / MARKET]' : 'Salida [STD / LIMIT]';
    } else {
      glowTheme = 'float';
      neonColorClass = 'border-slate-300 dark:border-slate-500 animate-stepped-glow-float';
      neonBgClass = 'bg-slate-50/10 dark:bg-slate-800/20';
      neonTextColor = 'text-slate-500 dark:text-slate-400';
      statusText = 'Salida [S/ ORDEN]';
    }
  }

  // Tensor bar: width proportional to pnl intensity, min 8px
  const barWidthPx = 8 + pnlIntensity * 80

  return (
    <div className={`group relative flex flex-col gap-0 transition-all duration-300`}>
      {/* Index pill */}
      <div className="flex items-center gap-3 mb-2">
        <span className="w-6 h-6 flex-shrink-0 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-500 dark:text-slate-400">
          {index + 1}
        </span>
        <span className="text-[10px] text-slate-400 dark:text-slate-500">{formatDateTime(trade.entry_datetime)}</span>
        {trade.duration_seconds > 0 && (
          <span className="flex items-center gap-1 text-[10px] text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-slate-900 px-1.5 py-0.5 rounded">
            <Clock className="w-3 h-3" />
            {formatDuration(trade.duration_seconds)}
          </span>
        )}
      </div>

      {/* Dumbbell row */}
      <div
        className={`rounded-xl border transition-all duration-200 overflow-hidden
          ${positive
            ? 'border-emerald-200/70 dark:border-emerald-800/50 bg-white dark:bg-gray-900/80 hover:border-emerald-400/60'
            : 'border-rose-200/70 dark:border-rose-800/50 bg-white dark:bg-gray-900/80 hover:border-rose-400/60'
          }
          group-hover:shadow-lg
        `}
      >
        <div className="flex items-stretch">
          {/* LEFT: Entry */}
          <div className="flex-1 px-5 py-4 border-r border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-400">
                Entrada
              </span>
              <OriginatorBadge originator={trade.originator} />
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white tabular-nums">
              {formatPrice(trade.entry_price)}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {formatAmount(trade.entry_amount)} <span className="font-semibold text-slate-700 dark:text-slate-300 uppercase">{trade.symbol}</span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <OrderIdBadge id={trade.entry_order_id} />
              <TypeTagBadges tags={trade.entry_order_tags} variant="entry" />
            </div>
          </div>

          {/* CENTER: Tensor bar */}
          <div className="flex flex-col items-center justify-center px-3 gap-1 bg-slate-50/50 dark:bg-slate-800/30 min-w-[80px]">
            <div className="flex flex-col items-center gap-0.5">
              <div
                className={`rounded-full transition-all duration-500 ${positive ? 'bg-emerald-400/70' : 'bg-rose-400/70'}`}
                style={{ width: `${barWidthPx}px`, height: '4px' }}
              />
              <ArrowRight className={`w-4 h-4 ${positive ? 'text-emerald-500' : 'text-rose-500'}`} />
              <div
                className={`rounded-full transition-all duration-500 ${positive ? 'bg-emerald-400/70' : 'bg-rose-400/70'}`}
                style={{ width: `${barWidthPx}px`, height: '4px' }}
              />
            </div>
          </div>

          {/* RIGHT: Exit */}
          <div className="flex-1 px-5 py-4 border-l border-slate-100 dark:border-slate-800 relative overflow-hidden group/exit">
            
            {/* Latido 'Intro Motorola' / Vivo si está abierta */}
            {isExitOpen && (
              <>
                <div className={`absolute inset-0 ${neonBgClass} pointer-events-none`} />
                <div 
                  className={`absolute inset-[2px] rounded-lg border-2 pointer-events-none ${neonColorClass}`}
                />
              </>
            )}

            <div className="relative z-10 flex flex-col justify-center h-full">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-[10px] font-bold uppercase tracking-widest ${isExitOpen ? neonTextColor : 'text-amber-600 dark:text-amber-400'}`}>
                  {isExitOpen ? statusText : 'Salida'}
                </span>
                {isExitOpen && glowTheme !== 'float' && (
                  <span className="text-[10px] font-bold italic opacity-60 ml-2 animate-pulse">• Waiting Match</span>
                )}
              </div>
              
              <div className="text-lg font-bold text-gray-900 dark:text-white tabular-nums">
                {trade.exit_price ? formatPrice(trade.exit_price) : '-'}
              </div>
              
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                {formatAmount(trade.exit_amount ?? 0)} <span className="font-semibold uppercase text-slate-700 dark:text-slate-300">{trade.symbol}</span>
              </div>
              
              <div className="flex items-center flex-wrap gap-2 mt-2">
                {trade.exit_order_id && <OrderIdBadge id={trade.exit_order_id} />}
                {trade.exit_order_tags && trade.exit_order_tags.length > 0 && (
                  <TypeTagBadges tags={trade.exit_order_tags} variant="exit" />
                )}
              </div>
            </div>
          </div>

          {/* FAR RIGHT: PnL */}
          <div className="flex items-center justify-end px-5 py-4 min-w-[120px] border-l border-slate-100 dark:border-slate-800 relative z-20">
            {!isExitOpen ? (
               <PnlBadge pnl={trade.pnl_net} percentage={trade.pnl_percentage} />
            ) : (
               <div className="flex flex-col items-end gap-1">
                 <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right animate-pulse">Intent</span>
                 <PnlBadge pnl={trade.pnl_net} percentage={trade.pnl_percentage} />
               </div>
            )}
          </div>
        </div>

        {/* Fee strip */}
        <div className="px-5 py-1.5 bg-slate-50/80 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800/50 flex items-center gap-4">
          <span className="text-[10px] text-slate-400 dark:text-slate-500">
            Fee entrada: <span className="text-rose-400/80">-{formatAmount(trade.entry_fee)}</span>
          </span>
          {trade.exit_fee != null && (
            <span className="text-[10px] text-slate-400 dark:text-slate-500">
              Fee salida: <span className="text-rose-400/80">-{formatAmount(trade.exit_fee)}</span>
            </span>
          )}
          <ExpandToggle
            expanded={expanded}
            onToggle={() => setExpanded(!expanded)}
            hasFills={hasFills}
          />
        </div>

        {/* Expandable fills */}
        {expanded && hasFills && (
          <div className="px-5 py-3 border-t border-slate-100 dark:border-slate-800/50 bg-slate-50/30 dark:bg-slate-900/30">
            <FillsSubTable fills={trade.entry_fills} title="Entrada" />
            <FillsSubTable fills={trade.exit_fills} title="Salida" />
          </div>
        )}
      </div>
    </div>
  )
}

function OrphanCard({ trade }: { trade: Trade }) {
  return (
    <div className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-sm">
      <div className="flex items-center gap-4">
        <span className="px-2 py-1 bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded text-xs font-bold uppercase tracking-wider">
          Orphan 
        </span>
        <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          {formatAmount(trade.entry_amount)} {trade.symbol}
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-sm font-bold">{formatPrice(trade.entry_price)}</div>
          <div className="text-[10px] text-slate-400">{formatDateTime(trade.entry_datetime)}</div>
        </div>
        <div className="flex items-center gap-1">
           {trade.entry_order_id && <OrderIdBadge id={trade.entry_order_id} />}
           <TypeTagBadges tags={trade.entry_order_tags} variant="exit" />
        </div>
      </div>
    </div>
  )
}

export function IntentView({ trades, symbol }: Props) {
  // Filtramos trades
  const realTrades = trades.filter(t => !t.is_pending && !t.is_orphan);
  const orphanOrders = trades.filter(t => t.is_orphan);

  return (
    <div className="p-6 flex flex-col gap-8">
      {/* Definición de animación robótica / con 'menos frames' y super glow en colores */}
      <style>{`
        @keyframes heartbeat-glow {
          0%, 100% { transform: scale(1); filter: brightness(1) drop-shadow(0 0 5px currentColor); }
          10% { transform: scale(1.02); filter: brightness(1.5) drop-shadow(0 0 20px currentColor); }
          20% { transform: scale(1); filter: brightness(1) drop-shadow(0 0 5px currentColor); }
          30% { transform: scale(1.05); filter: brightness(1.8) drop-shadow(0 0 30px currentColor); }
          40% { transform: scale(1); filter: brightness(1) drop-shadow(0 0 5px currentColor); }
        }

        /* ALGO: Amber Glow */
        @keyframes stepped-glow-algo {
          0%, 100% { opacity: 0.4; box-shadow: inset 0 0 15px rgba(251,191,36,0.1), 0 0 10px rgba(245,158,11,0.2); border-color: rgba(251,191,36,0.2); }
          50% { opacity: 1; box-shadow: inset 0 0 40px rgba(251,191,36,0.5), 0 0 50px rgba(245,158,11,0.8); border-color: rgba(251,191,36,0.8); }
        }
        .animate-stepped-glow-algo { animation: stepped-glow-algo 2s steps(8, end) infinite; }

        /* STANDARD: Sky/Blue Glow */
        @keyframes stepped-glow-std {
          0%, 100% { opacity: 0.4; box-shadow: inset 0 0 15px rgba(14,165,233,0.1), 0 0 10px rgba(2,132,199,0.2); border-color: rgba(14,165,233,0.2); }
          50% { opacity: 1; box-shadow: inset 0 0 40px rgba(14,165,233,0.5), 0 0 50px rgba(2,132,199,0.8); border-color: rgba(14,165,233,0.8); }
        }
        .animate-stepped-glow-std { animation: stepped-glow-std 2s steps(8, end) infinite; }

        /* FLOATING: Slate/Gray Glow */
        @keyframes stepped-glow-float {
          0%, 100% { opacity: 0.3; box-shadow: none; border-color: rgba(148,163,184,0.2); }
          50% { opacity: 0.7; box-shadow: 0 0 20px rgba(148,163,184,0.3); border-color: rgba(148,163,184,0.5); }
        }
        .animate-stepped-glow-float { animation: stepped-glow-float 3s ease-in-out infinite; }
        
        .neon-pulse { animation: heartbeat-glow 4s infinite; }
      `}</style>

      {/* PAIRS SECTION */}
      <div className="flex flex-col gap-4">
        {/* Header legend */}
        <div className="flex items-center gap-6 text-[11px] text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-3">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-1 rounded-full bg-blue-400 inline-block" />
            Vista Intención — emparejamiento predictivo de montos exactos
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-1 rounded-full bg-emerald-400 inline-block" />
            Barra verde = PnL positivo
          </span>
        </div>

        {realTrades.length === 0 ? (
          <div className="p-12 text-center text-gray-400 dark:text-gray-500">
            <div className="text-4xl mb-3">🎯</div>
            <p className="text-sm">No hay posiciones estructuradas bajo el motor de Intención.</p>
          </div>
        ) : (
          realTrades.map((trade, i) => (
            <IntentCard key={trade.id} trade={trade} index={i} />
          ))
        )}
      </div>

      {/* ORPHANS SECTION */}
      {orphanOrders.length > 0 && (
        <div className="flex flex-col gap-4 pt-6 border-t border-slate-200 dark:border-slate-800/80">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-widest">
              Órdenes Huérfanas
            </h3>
            <span className="px-2 py-0.5 bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 rounded-full text-xs font-semibold">
              {orphanOrders.length}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {orphanOrders.map(orphan => (
              <OrphanCard key={orphan.id} trade={orphan} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
