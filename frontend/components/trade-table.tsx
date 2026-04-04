'use client'

import { Trade } from '@/lib/api'
import { format } from 'date-fns'
import { formatPrice, formatAmount, formatPercentage } from '@/lib/utils'

interface TradeTableProps {
  trades: Trade[]
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

export function TradeTable({ trades }: TradeTableProps) {
  if (trades.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 dark:text-gray-400">
        No hay operaciones registradas. Haz clic en "Sincronizar" para obtener tus trades de Binance.
      </div>
    )
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
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Entrada
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Salida
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Cantidad
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Precio Entrada
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Precio Salida
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Duración
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              PnL Neto
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              PnL %
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          {trades.map((trade, index) => (
            <tr
              key={trade.id || `trade-${index}`}
              className={`hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                trade.is_pending ? 'bg-purple-50 dark:bg-purple-900/20' :
                trade.is_orphan ? 'bg-orange-50 dark:bg-orange-900/20' : 
                (!trade.exit_datetime ? 'bg-blue-50 dark:bg-blue-900/20' : '')
              }`}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white align-top">
                <div className="flex flex-col">
                  <span className="font-medium">{formatDate(trade.entry_datetime)}</span>
                  <span className={`text-xs ${trade.entry_side === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                    {trade.entry_side.toUpperCase()}
                  </span>
                  <TypeTagBadges tags={trade.entry_order_tags} variant="entry" />
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white align-top">
                <div className="flex flex-col gap-1">
                  {trade.is_pending ? (
                    <span className="px-2 py-1 bg-purple-100 dark:bg-purple-800 text-purple-700 dark:text-purple-200 rounded text-xs font-bold">
                      PENDING {trade.order_type}
                    </span>
                  ) : trade.exit_datetime ? (
                    <div className="flex flex-col">
                      <span className="font-medium">{formatDate(trade.exit_datetime)}</span>
                      {trade.exit_side && (
                        <span className={`text-xs ${trade.exit_side === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                          {trade.exit_side.toUpperCase()}
                        </span>
                      )}
                    </div>
                  ) : trade.conditional_exit ? (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-xs font-semibold text-amber-700 dark:text-amber-300">
                        CONDITIONAL · {trade.conditional_exit.order_type}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-300">
                        Trigger {formatPrice(trade.conditional_exit.trigger_price)} ·{' '}
                        {trade.conditional_exit.side.toUpperCase()}
                      </span>
                      {trade.conditional_exit.conditional_kind ? (
                        <span className="text-[10px] uppercase text-gray-500 dark:text-gray-400">
                          {trade.conditional_exit.conditional_kind.replace(/_/g, ' ')}
                        </span>
                      ) : null}
                      <span className="text-[10px] text-gray-400 dark:text-gray-500 font-mono">
                        algo #{trade.conditional_exit.algo_id}
                      </span>
                    </div>
                  ) : (
                    <span className="text-gray-500 italic">
                      {trade.is_orphan ? 'Orphan (unmatched)' : 'Open (floating)'}
                    </span>
                  )}
                  <TypeTagBadges tags={trade.exit_order_tags} variant="exit" />
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {formatAmount(trade.entry_amount)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {formatPrice(trade.entry_price)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {trade.is_pending ? (
                  <span className="font-bold text-purple-600 dark:text-purple-400">
                    {formatPrice(trade.entry_price)}
                  </span>
                ) : (
                  formatPrice(trade.exit_price)
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {trade.duration_seconds > 0 ? formatDuration(trade.duration_seconds) : <span className="text-gray-500">—</span>}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {trade.is_pending ? (
                  <span className="text-gray-400">—</span>
                ) : (
                  <div className="flex flex-col">
                    <span className={`font-semibold ${trade.pnl_net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPrice(trade.pnl_net)}
                    </span>
                    {!trade.exit_datetime && (
                      <div className="flex gap-2 mt-1 text-[10px]">
                        {trade.tp_pnl !== null && trade.tp_pnl !== undefined ? (
                          <span className="text-green-500 bg-green-50 dark:bg-green-900/30 px-1 rounded border border-green-200 dark:border-green-800">
                            TP: {formatPrice(trade.tp_pnl)}
                          </span>
                        ) : (
                          <span className="text-gray-400 bg-gray-100 dark:bg-gray-800 px-1 rounded border border-gray-200 dark:border-gray-700" title="No TP order found">
                            TP: ⚠️
                          </span>
                        )}
                        {trade.sl_pnl !== null && trade.sl_pnl !== undefined ? (
                          <span className="text-red-500 bg-red-50 dark:bg-red-900/30 px-1 rounded border border-red-200 dark:border-red-800">
                            SL: {formatPrice(trade.sl_pnl)}
                          </span>
                        ) : (
                          <span className="text-gray-400 bg-gray-100 dark:bg-gray-800 px-1 rounded border border-gray-200 dark:border-gray-700" title="No SL order found">
                            SL: ⚠️
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${
                trade.is_pending ? 'text-gray-400' :
                (trade.pnl_percentage >= 0 ? 'text-green-600' : 'text-red-600')
              }`}>
                {trade.is_pending ? '—' : formatPercentage(trade.pnl_percentage)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
