'use client'

import { Trade } from '@/lib/api'
import { formatPrice } from '@/lib/utils'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ReferenceLine,
} from 'recharts'
import { format } from 'date-fns'

interface TradeChartProps {
  trades: Trade[]
}

export function TradeChart({ trades }: TradeChartProps) {
  if (trades.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
        No hay datos para mostrar
      </div>
    )
  }

  // Prepare data for the chart
  // Show entry and exit prices over time
  const chartData = trades
    .map((trade) => [
      {
        time: format(new Date(trade.entry_datetime), 'MM/dd HH:mm'),
        timestamp: new Date(trade.entry_datetime).getTime(),
        price: trade.entry_price,
        type: 'entry',
        side: trade.entry_side,
        pnl: trade.pnl_net,
      },
      {
        time: trade.exit_datetime ? format(new Date(trade.exit_datetime), 'MM/dd HH:mm') : 'Open',
        timestamp: trade.exit_datetime ? new Date(trade.exit_datetime).getTime() : Date.now(),
        price: trade.exit_price || trade.entry_price,
        type: 'exit',
        side: trade.exit_side || trade.entry_side,
        pnl: trade.pnl_net,
      },
    ])
    .flat()
    .sort((a, b) => a.timestamp - b.timestamp)

  // Calculate price range for better visualization
  const prices = trades.flatMap((t) => [t.entry_price, t.exit_price ?? t.entry_price])
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice
  const yAxisDomain = [
    minPrice - priceRange * 0.1,
    maxPrice + priceRange * 0.1,
  ]

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis
            dataKey="time"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            domain={yAxisDomain}
            tick={{ fontSize: 12 }}
            label={{ value: 'Precio (USDT)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload
                return (
                  <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
                    <p className="font-semibold">{data.time}</p>
                    <p className={`${data.type === 'entry' ? 'text-blue-600' : 'text-purple-600'}`}>
                      {data.type === 'entry' ? 'Entrada' : 'Salida'}: {formatPrice(data.price)}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Lado: {data.side.toUpperCase()}
                    </p>
                    {data.pnl !== undefined && (
                      <p className={`text-sm font-semibold ${data.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        PnL: {formatPrice(data.pnl)}
                      </p>
                    )}
                  </div>
                )

              }
              return null
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Precio"
          />
          {/* Mark entry points */}
          {chartData
            .filter((d) => d.type === 'entry')
            .map((point, idx) => (
              <ReferenceLine
                key={`entry-${idx}`}
                x={point.time}
                stroke={point.side === 'buy' ? '#10b981' : '#ef4444'}
                strokeDasharray="3 3"
                strokeWidth={1}
              />
            ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
