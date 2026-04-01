'use client'

import React, { useState } from 'react'
import { useBalances } from '@/hooks/use-trades'
import { clsx } from 'clsx'

type Tab = 'totals' | 'futures' | 'spot'

export function BalanceWidget() {
  const { data: balances, isLoading, isError } = useBalances()
  const [activeTab, setActiveTab] = useState<Tab>('totals')

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700 animate-pulse h-48 flex items-center justify-center">
        <span className="text-gray-400">Cargando saldos...</span>
      </div>
    )
  }

  if (isError || !balances) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700 flex items-center justify-center h-48">
        <span className="text-rose-400">Error cargando saldos.</span>
      </div>
    )
  }

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'totals', label: 'Total', icon: '💰' },
    { id: 'futures', label: 'Futures', icon: '📈' },
    { id: 'spot', label: 'Spot', icon: '👛' },
  ]

  // Choose the data slice based on the active tab
  const getDisplayData = () => {
    if (activeTab === 'totals') {
      return Object.entries(balances.totals).map(([asset, amount]) => ({
        asset,
        free: balances.futures[asset]?.free ?? 0,
        used: balances.futures[asset]?.used ?? 0,
        total: amount,
      }))
    }
    
    const slice = balances[activeTab]
    return Object.entries(slice).map(([asset, bal]) => ({
      asset,
      free: bal.free,
      used: bal.used,
      total: bal.total,
    }))
  }

  const data = getDisplayData().sort((a, b) => b.total - a.total)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden relative">
      <div className="p-6">
         <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg text-indigo-600 dark:text-indigo-400">
                💼
              </span>
              Saldos (Balance)
            </h3>
            
            {/* Tabs */}
            <div className="flex bg-gray-100 dark:bg-gray-900/50 p-1 rounded-lg">
               {tabs.map(tab => (
                 <button
                   key={tab.id}
                   onClick={() => setActiveTab(tab.id)}
                   className={clsx(
                     "px-3 py-1 text-xs font-bold rounded-md transition-all flex items-center gap-1.5",
                     activeTab === tab.id 
                       ? "bg-white dark:bg-gray-700 text-indigo-600 dark:text-indigo-400 shadow-sm" 
                       : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                   )}
                 >
                   <span>{tab.icon}</span>
                   {tab.label}
                 </button>
               ))}
            </div>
         </div>

         {/* Balance List */}
         {data.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-sm">
               No hay saldos superiores a 0.1 USD en esta billetera.
            </div>
         ) : (
            <div className="space-y-3">
               {data.map((item) => (
                 <div key={item.asset} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900/40 rounded-xl border border-gray-100 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-600 transition-colors">
                    <div className="flex items-center gap-3">
                       <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs shadow-inner">
                          {item.asset.substring(0, 3)}
                       </div>
                       <div>
                          <p className="font-bold text-gray-900 dark:text-white text-sm">{item.asset}</p>
                          <p className="text-[10px] text-gray-500 font-mono flex gap-2">
                             <span>Libre: {item.free.toLocaleString(undefined, {maximumFractionDigits: 4})}</span>
                             {item.used > 0 && <span className="text-amber-500">En Orden: {item.used.toLocaleString(undefined, {maximumFractionDigits: 4})}</span>}
                          </p>
                       </div>
                    </div>
                    <div className="text-right">
                       <p className="font-bold text-indigo-600 dark:text-indigo-400 text-sm font-mono">
                          {item.total.toLocaleString(undefined, {maximumFractionDigits: 4})}
                       </p>
                    </div>
                 </div>
               ))}
            </div>
         )}
      </div>
      
      {/* Decorative background shape */}
      <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-gradient-to-br from-indigo-500/10 to-teal-500/10 blur-2xl rounded-full pointer-events-none" />
    </div>
  )
}
