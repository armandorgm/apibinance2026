'use client'

/**
 * PositionHistory — Router Component
 *
 * Lee la prop `logic` (método) y decide qué vista montar.
 * Actúa como orquestador, manteniendo unificada la API hacia el componente padre (`page.tsx`).
 */

import React from 'react'
import { Trade } from '@/lib/api'
import { MethodKey } from './method-selector'

import { AtomicFifoView } from './atomic-fifo-view'
import { AtomicLifoView } from './atomic-lifo-view'
import { FifoView } from './fifo-view'
import { LifoView } from './lifo-view'
import { IntentView } from './intent-view'

interface Props {
  trades: Trade[]
  logic: string
  isLoading: boolean
  symbol: string
}

export function PositionHistory({ trades, logic, isLoading, symbol }: Props) {
  if (isLoading) {
    return (
      <div className="p-12 text-center text-gray-500 dark:text-gray-400 animate-pulse">
        Cargando historial de posiciones...
      </div>
    )
  }

  // Router logic
  switch (logic as MethodKey) {
    case 'atomic_fifo':
      return <AtomicFifoView trades={trades} symbol={symbol} />
    case 'atomic_lifo':
      return <AtomicLifoView trades={trades} />
    case 'fifo':
      return <FifoView trades={trades} />
    case 'lifo':
      return <LifoView trades={trades} />
    case 'intent_fifo':
      return <IntentView trades={trades} symbol={symbol} />
    default:
      // Fallback
      return (
        <div className="p-8 text-center text-rose-500 bg-rose-50 dark:bg-rose-900/10 rounded-xl">
          Error: Método de representación desconocido ({logic})
        </div>
      )
  }
}
