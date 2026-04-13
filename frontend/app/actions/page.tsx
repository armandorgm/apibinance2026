'use client'

import { useSearchParams } from 'next/navigation'
import { UcoeActionForm } from '@/components/actions/ucoe-action-form'
import { ChaseEntryForm, MarketBuyForm } from '@/components/actions/trading-forms'
import { Suspense } from 'react'
import { Loader2 } from 'lucide-react'

function ActionsDispatcher() {
  const searchParams = useSearchParams()
  const type = searchParams.get('type') || 'chase-entry'
  const symbol = searchParams.get('symbol') || '1000PEPEUSDC'

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      {type === 'ucoe' && <UcoeActionForm initialSymbol={symbol} />}
      {type === 'chase-entry' && <ChaseEntryForm symbol={symbol} />}
      {type === 'market-buy' && <MarketBuyForm symbol={symbol} />}
      
      {/* Fallback for actions in migration process */}
      {!['ucoe', 'chase-entry', 'market-buy'].includes(type) && (
        <div className="p-20 text-center bg-white dark:bg-gray-900 rounded-[2.5rem] border-2 border-dashed border-gray-100 dark:border-gray-800 flex flex-col items-center gap-6 shadow-sm">
          <div className="w-20 h-20 rounded-3xl bg-gray-50 dark:bg-gray-950 flex items-center justify-center text-gray-300 dark:text-gray-700 shadow-inner">
            <Loader2 className="w-10 h-10 animate-spin" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-2 tracking-tight">Acción en Camino</h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-xs mx-auto text-sm">
              Estamos migrando la lógica de <span className="font-bold text-indigo-500">"{type}"</span> a este nuevo panel de control modular.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ActionsPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="w-12 h-12 animate-spin text-indigo-500" />
        <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">Cargando Acción...</p>
      </div>
    }>
      <ActionsDispatcher />
    </Suspense>
  )
}
