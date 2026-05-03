'use client'

import Link from 'next/link'
import { usePathname, useSearchParams } from 'next/navigation'
import { Zap, ShoppingCart, Wrench, Play, History, ChevronRight, LayoutDashboard } from 'lucide-react'

const CATEGORIES = [
  {
    name: 'Operaciones',
    items: [
      { id: 'chase-entry', name: 'Chase Entry', icon: Zap, color: 'text-amber-500' },
      { id: 'market-buy', name: 'Market Buy', icon: ShoppingCart, color: 'text-emerald-500' },
      { id: 'ucoe', name: 'Unified Counter-Order Engine (UCOE)', icon: Wrench, color: 'text-indigo-500' },
    ]
  },
  {
    name: 'Mantenimiento',
    items: [
      { id: 'historical-sync', name: 'Sincronización Histórica', icon: History, color: 'text-violet-500' },
    ]
  },
  {
    name: 'Sistema',
    items: [
      { id: 'bot-control', name: 'Control de Bot', icon: Play, color: 'text-blue-500' },
    ]
  }
]

export function ActionsSidebar() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const currentAction = searchParams.get('type') || 'chase-entry'

  return (
    <aside className="w-72 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col h-screen sticky top-0">
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <Link 
          href="/"
          className="flex items-center gap-2 text-gray-500 hover:text-indigo-600 transition-colors mb-4 group"
        >
          <LayoutDashboard className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-bold uppercase tracking-wider">Dashboard</span>
        </Link>
        <h2 className="text-2xl font-black bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
          Acciones
        </h2>
      </div>

      <nav className="flex-1 overflow-y-auto p-4 space-y-8">
        {CATEGORIES.map((category) => (
          <div key={category.name} className="space-y-2">
            <h3 className="px-4 text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 dark:text-gray-500">
              {category.name}
            </h3>
            <div className="space-y-1">
              {category.items.map((item) => {
                const isActive = currentAction === item.id
                return (
                  <Link
                    key={item.id}
                    href={`/actions?type=${item.id}`}
                    className={`
                      flex items-center justify-between px-4 py-3 rounded-xl transition-all group
                      ${isActive 
                        ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 font-bold shadow-sm' 
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3">
                      <item.icon className={`w-5 h-5 ${item.color} ${isActive ? 'fill-current opacity-20' : ''}`} />
                      <span className="text-sm">{item.name}</span>
                    </div>
                    {isActive && <ChevronRight className="w-4 h-4" />}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="p-6 border-t border-gray-200 dark:border-gray-800">
        <div className="p-4 rounded-2xl bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-900/50 shadow-inner">
          <p className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mb-1">
            Propiedad de Antigravity
          </p>
          <p className="text-[10px] text-indigo-600/70 dark:text-indigo-400/60 leading-relaxed italic">
            Diseñé, Implementé y Lancé este sistema de reparación segura.
          </p>
        </div>
      </div>
    </aside>
  )
}
