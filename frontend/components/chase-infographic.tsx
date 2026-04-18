'use client'

import React from 'react'
import { ActivePipeline } from '@/lib/api'
import { formatPrice } from '@/lib/utils'
import { clsx } from 'clsx'
import { 
  ArrowRight, 
  CheckCircle2, 
  RefreshCcw, 
  Target, 
  AlertCircle,
  Timer,
  Zap,
  TrendingUp,
  TrendingDown
} from 'lucide-react'

import { useNotifications } from '@/components/notification-provider'

interface ChaseInfographicProps {
  pipeline: ActivePipeline
}

export function ChaseInfographic({ pipeline }: ChaseInfographicProps) {
  const { prices } = useNotifications()
  
  const { 
    symbol,
    status, 
    sub_status, 
    retry_count, 
    last_tick_price, 
    last_order_price, 
    side, 
    finished_at 
  } = pipeline

  // Priorizar precio en vivo del WebSocket si está disponible
  const livePriceData = prices[symbol]
  const currentLivePrice = livePriceData?.last || last_tick_price
  const isLive = !!livePriceData

  const isFinished = status === 'COMPLETED' || status === 'ABORTED'
  const isAborted = status === 'ABORTED'
  
  // Calculate price distance in ticks-like percentage
  const priceDist = currentLivePrice && last_order_price 
    ? ((currentLivePrice - last_order_price) / last_order_price) * 100 
    : 0

  const steps = [
    { 
      id: 'INIT', 
      label: 'Inicio', 
      icon: Zap,
      active: ['INIT', 'RECOVERING', 'CHASING', 'WAITING_FILL', 'DONE'].includes(sub_status)
    },
    { 
      id: 'CHASING', 
      label: 'Persecución', 
      icon: RefreshCcw, 
      active: ['CHASING', 'WAITING_FILL', 'DONE'].includes(sub_status),
      pulse: sub_status === 'CHASING' || sub_status === 'RECOVERING'
    },
    { 
      id: 'WAITING_FILL', 
      label: 'Mercado', 
      icon: Timer, 
      active: ['DONE'].includes(sub_status) || (status === 'CHASING' && sub_status === 'WAITING_FILL'),
      pulse: status === 'CHASING' && sub_status === 'WAITING_FILL'
    },
    { 
      id: 'DONE', 
      label: 'Take Profit', 
      icon: Target, 
      active: sub_status === 'DONE' && !isAborted
    }
  ]

  return (
    <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900/40 rounded-2xl border border-gray-100 dark:border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className={clsx(
            "p-2 rounded-lg",
            isFinished ? (isAborted ? "bg-rose-100 text-rose-600" : "bg-emerald-100 text-emerald-600") : "bg-indigo-100 text-indigo-600 animate-pulse"
          )}>
            {isFinished ? (isAborted ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />) : <RefreshCcw size={18} className="animate-spin-slow" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-gray-900 dark:text-white">
                {isFinished ? (isAborted ? 'Proceso Abortado' : 'Chase Completado') : 'Persiguiendo Precio...'}
              </h4>
              {isLive && !isFinished && (
                <div className="flex items-center gap-1 px-1.5 py-0.5 bg-rose-500/10 text-rose-500 rounded text-[8px] font-black animate-pulse border border-rose-500/20">
                  <div className="w-1 h-1 bg-rose-500 rounded-full" />
                  LIVE
                </div>
              )}
            </div>
            <p className="text-[10px] text-gray-500 uppercase font-semibold">
               Sub-Estado: <span className="text-indigo-500">{sub_status}</span>
            </p>
          </div>
        </div>
        
        {retry_count > 0 && (
          <div className="flex items-center gap-1.5 px-2 py-1 bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 rounded-md border border-amber-100 dark:border-amber-800/50">
            <RefreshCcw size={12} />
            <span className="text-[10px] font-bold">REINTENTOS: {retry_count}</span>
          </div>
        )}
      </div>

      {/* Progress Timeline */}
      <div className="relative flex justify-between items-center px-2 mb-6">
        <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 dark:bg-gray-800 -translate-y-1/2 z-0" />
        
        {steps.map((step, idx) => {
          const Icon = step.icon
          const isActive = step.active
          const isPulse = step.pulse

          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center">
              <div className={clsx(
                "w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 border-2",
                isActive 
                  ? "bg-white dark:bg-gray-800 border-indigo-500 text-indigo-500 shadow-lg shadow-indigo-500/20" 
                  : "bg-gray-100 dark:bg-gray-900 border-gray-200 dark:border-gray-800 text-gray-400",
                isPulse && "animate-pulse ring-4 ring-indigo-500/20"
              )}>
                <Icon size={20} className={clsx(isPulse && "animate-spin-slow")} />
              </div>
              <span className={clsx(
                "text-[10px] font-bold mt-2",
                isActive ? "text-gray-900 dark:text-white" : "text-gray-400"
              )}>
                {step.label}
              </span>
            </div>
          )
        })}
      </div>

      {/* Real-time Distance Metrics */}
      {!isFinished && currentLivePrice && last_order_price && (
        <div className="grid grid-cols-2 gap-3 p-3 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
          <div className="flex flex-col">
            <span className="text-[9px] text-gray-500 uppercase font-bold tracking-wider mb-1">Tu Orden</span>
            <div className="flex items-center gap-2">
               <span className="text-sm font-mono font-bold text-gray-900 dark:text-white">
                {formatPrice(last_order_price, '')}
               </span>
               <div className={clsx("p-0.5 rounded text-[8px] font-bold", side === 'buy' ? "bg-emerald-100 text-emerald-600" : "bg-rose-100 text-rose-600")}>
                  {side?.toUpperCase()}
               </div>
            </div>
          </div>
          
          <div className="flex flex-col border-l border-gray-100 dark:border-gray-700 pl-3">
             <div className="flex items-center justify-between">
                <span className="text-[9px] text-gray-500 uppercase font-bold tracking-wider">Brecha Arena</span>
                {priceDist !== 0 && (
                   <div className={clsx(
                     "flex items-center text-[9px] font-bold",
                     priceDist > 0 ? "text-emerald-500" : "text-rose-500"
                   )}>
                     {priceDist > 0 ? <TrendingUp size={10} className="mr-0.5" /> : <TrendingDown size={10} className="mr-0.5" />}
                     {Math.abs(priceDist).toFixed(3)}%
                   </div>
                 )}
             </div>
             <div className="text-sm font-mono font-bold text-indigo-500">
               {formatPrice(currentLivePrice, '')}
             </div>
          </div>
        </div>
      )}

      {isFinished && finished_at && (
        <div className="text-center py-1">
          <p className="text-[10px] text-gray-400 italic">
            Finalizado a las {new Date(finished_at).toLocaleTimeString()}
          </p>
        </div>
      )}

    </div>
  )
}
