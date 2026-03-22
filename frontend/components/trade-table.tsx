'use client'

import { Trade } from '@/lib/api'
import { format } from 'date-fns'

interface TradeTableProps {
  trades: Trade[]
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
          {trades.map((trade) => (
            <tr
              key={trade.id}
              className={`hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                trade.is_orphan ? 'bg-orange-50 dark:bg-orange-900/20' : 
                (!trade.exit_datetime ? 'bg-blue-50 dark:bg-blue-900/20' : '')
              }`}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                <div className="flex flex-col">
                  <span className="font-medium">{formatDate(trade.entry_datetime)}</span>
                  <span className={`text-xs ${trade.entry_side === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                    {trade.entry_side.toUpperCase()}
                  </span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {trade.exit_datetime ? (
                  <div className="flex flex-col">
                    <span className="font-medium">{formatDate(trade.exit_datetime)}</span>
                    {trade.exit_side && (
                      <span className={`text-xs ${trade.exit_side === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.exit_side.toUpperCase()}
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="text-gray-500 italic">
                    {trade.is_orphan ? 'Orphan (unmatched)' : 'Open (floating)'}
                  </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {trade.entry_amount.toFixed(6)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                ${trade.entry_price.toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : <span className="text-gray-500">—</span>}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {trade.duration_seconds > 0 ? formatDuration(trade.duration_seconds) : <span className="text-gray-500">—</span>}
              </td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${
                trade.pnl_net >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${trade.pnl_net.toFixed(2)}
              </td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${
                trade.pnl_percentage >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {trade.pnl_percentage >= 0 ? '+' : ''}{trade.pnl_percentage.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
