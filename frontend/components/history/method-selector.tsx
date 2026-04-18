'use client'

import React from 'react'

export type MethodKey = 'atomic_fifo' | 'atomic_lifo' | 'fifo' | 'lifo' | 'intent_fifo'

interface MethodConfig {
  key: MethodKey
  label: string
  shortLabel: string
  icon: string
  description: string
  accentColor: string
  bgActive: string
  borderActive: string
  textActive: string
  ringColor: string
}

const METHODS: MethodConfig[] = [
  {
    key: 'atomic_fifo',
    label: 'Atomic FIFO',
    shortLabel: 'FIFO Exacto',
    icon: '⚖️',
    description: 'Empareja órdenes con cantidad exacta. 1 compra = 1 venta perfecta.',
    accentColor: '#3B82F6',
    bgActive: 'bg-blue-600',
    borderActive: 'border-blue-500',
    textActive: 'text-white',
    ringColor: 'ring-blue-500/30',
  },
  {
    key: 'atomic_lifo',
    label: 'Atomic LIFO',
    shortLabel: 'LIFO Exacto',
    icon: '📚',
    description: 'Igual que Atomic pero cierra primero el trade más reciente con cantidad exacta.',
    accentColor: '#8B5CF6',
    bgActive: 'bg-violet-600',
    borderActive: 'border-violet-500',
    textActive: 'text-white',
    ringColor: 'ring-violet-500/30',
  },
  {
    key: 'fifo',
    label: 'FIFO Puro',
    shortLabel: 'FIFO Parciales',
    icon: '📦',
    description: 'Contabilidad clásica: los lotes más antiguos se consumen primero, soporta parciales.',
    accentColor: '#10B981',
    bgActive: 'bg-emerald-600',
    borderActive: 'border-emerald-500',
    textActive: 'text-white',
    ringColor: 'ring-emerald-500/30',
  },
  {
    key: 'lifo',
    label: 'LIFO Puro',
    shortLabel: 'LIFO Parciales',
    icon: '⚡',
    description: 'Scalping: los trades más recientes se cierran primero, soporta parciales.',
    accentColor: '#F59E0B',
    bgActive: 'bg-amber-600',
    borderActive: 'border-amber-500',
    textActive: 'text-white',
    ringColor: 'ring-amber-500/30',
  },
  {
    key: 'intent_fifo',
    label: 'Intent Matcher',
    shortLabel: 'Bracket (Intent)',
    icon: '🎯',
    description: 'Monitor de intención. Busca hacia el futuro emparejando órdenes 1 a 1 para mostrar el bracket (TP) de tu entrada.',
    accentColor: '#F43F5E', // Rose/Pink
    bgActive: 'bg-rose-600',
    borderActive: 'border-rose-500',
    textActive: 'text-white',
    ringColor: 'ring-rose-500/30',
  },
]

interface MethodSelectorProps {
  value: MethodKey
  onChange: (method: MethodKey) => void
}

export function MethodSelector({ value, onChange }: MethodSelectorProps) {
  const active = METHODS.find((m) => m.key === value) ?? METHODS[0]

  return (
    <div className="flex flex-col gap-2">
      <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
        Método de representación
      </label>

      {/* Pill tabs */}
      <div className="inline-flex rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800/60 p-1 gap-1">
        {METHODS.map((m) => {
          const isActive = m.key === value
          return (
            <button
              key={m.key}
              onClick={() => onChange(m.key)}
              title={m.description}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200
                ${isActive
                  ? `${m.bgActive} ${m.textActive} shadow-md ring-2 ${m.ringColor} scale-[1.02]`
                  : 'text-gray-600 dark:text-gray-400 hover:bg-white dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }
              `}
            >
              <span className="text-base leading-none">{m.icon}</span>
              <span className="hidden sm:inline">{m.shortLabel}</span>
            </button>
          )
        })}
      </div>

      {/* Contextual description */}
      <div
        className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-gray-600 dark:text-gray-300 border"
        style={{ borderColor: active.accentColor + '40', backgroundColor: active.accentColor + '0D' }}
      >
        <span className="text-base">{active.icon}</span>
        <div>
          <span className="font-bold" style={{ color: active.accentColor }}>{active.label}</span>
          {' — '}
          {active.description}
        </div>
      </div>
    </div>
  )
}

export { METHODS }
export type { MethodConfig }
