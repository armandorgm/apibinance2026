'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { 
  ChevronDown, Terminal, Zap, Activity, Route, 
  ListOrdered, Settings, Orbit, Sparkles, Menu, History,
  ShoppingCart, RefreshCw
} from 'lucide-react'
import { syncTrades } from '@/lib/api'
import { useNotifications } from '@/components/notification-provider'
import { Bell, BellOff, Wifi, WifiOff } from 'lucide-react'

export function DeveloperHubDropdown() {
  const [isOpen, setIsOpen] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const { settings, updateSettings, connectionStatus, requestPermissions } = useNotifications()
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Cierra el menu al clickear afuera
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  return (
    <div className="fixed top-4 right-4 z-[100]" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center w-10 h-10 bg-gray-900/80 dark:bg-gray-800/80 hover:bg-gray-800 dark:hover:bg-gray-700 text-gray-300 hover:text-white rounded-full backdrop-blur-md transition-all shadow-md active:scale-95 border border-gray-700/50 dark:border-gray-600/50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        title="Developer Hub"
      >
        <Menu className="w-5 h-5 text-indigo-400" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 rounded-2xl shadow-2xl bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border border-gray-100 dark:border-gray-700 ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 dark:divide-gray-800 overflow-hidden transform transition-all duration-200 origin-top-right">
          
          <div className="py-2">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Visualizaciones
            </div>
            <Link 
              href="/intent-timeline" 
              onClick={() => setIsOpen(false)}
              className="group flex items-center px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-amber-50 dark:hover:bg-amber-900/40 transition-colors"
            >
              <div className="mr-3 flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
                <Zap className="h-4 w-4" />
              </div>
              <div>
                <p className="font-semibold text-amber-600 dark:text-amber-400">Intent Timeline</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Atomic Matching 1:1</p>
              </div>
            </Link>

            <Link 
              href="/history-preview" 
              onClick={() => setIsOpen(false)}
              className="group flex items-center px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-indigo-900/40 transition-colors"
            >
              <div className="mr-3 flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                <History className="h-4 w-4" />
              </div>
              <div>
                <p className="font-semibold text-indigo-600 dark:text-indigo-400">History Preview</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Explorador de Trades</p>
              </div>
            </Link>
          </div>

          <div className="py-2">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Acciones Estratégicas
            </div>
            
            <Link 
              href="/actions?type=ucoe" 
              onClick={() => setIsOpen(false)}
              className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <Orbit className="mr-3 h-5 w-5 text-gray-400 group-hover:text-indigo-500" />
              UCOE Engine
            </Link>

            <Link 
              href="/actions?type=chase-entry" 
              onClick={() => setIsOpen(false)}
              className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <Zap className="mr-3 h-5 w-5 text-gray-400 group-hover:text-amber-500 whitespace-nowrap" />
              Chase Entry (OTO)
            </Link>

            <Link 
              href="/actions?type=market-buy" 
              onClick={() => setIsOpen(false)}
              className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <ShoppingCart className="mr-3 h-5 w-5 text-gray-400 group-hover:text-emerald-500" />
              Market Buy ($5)
            </Link>
          </div>

          <div className="py-2">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Control Bot
            </div>
            
            <Link href="/pipelines" onClick={() => setIsOpen(false)} className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
              <Route className="mr-3 h-5 w-5 text-gray-400 group-hover:text-blue-500" />
              Pipelines
            </Link>
            
            <Link href="/orders" onClick={() => setIsOpen(false)} className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
              <ListOrdered className="mr-3 h-5 w-5 text-gray-400 group-hover:text-purple-500" />
              Monitor Órdenes
            </Link>

            <button 
              onClick={async () => {
                try {
                  setSyncing(true)
                  await syncTrades('1000PEPEUSDC')
                  alert('Sincronización completada con éxito.')
                } catch (e: any) {
                  alert(`Error: ${e.message}`)
                } finally {
                  setSyncing(false)
                  setIsOpen(false)
                }
              }} 
              disabled={syncing}
              className="w-full group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
            >
              <RefreshCw className={`mr-3 h-5 w-5 text-gray-400 group-hover:text-sky-500 ${syncing ? 'animate-spin' : ''}`} />
              Sincronizar Ahora
            </button>
          </div>

          <div className="py-2">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex justify-between items-center">
              Notificaciones
              <div className="flex items-center gap-1">
                {connectionStatus === 'connected' ? (
                  <Wifi className="h-3 w-3 text-emerald-500" />
                ) : (
                  <WifiOff className="h-3 w-3 text-red-500 animate-pulse" />
                )}
                <span className={`text-[10px] ${connectionStatus === 'connected' ? 'text-emerald-500' : 'text-red-500'}`}>
                  {connectionStatus === 'connected' ? 'LIVE' : 'OFF'}
                </span>
              </div>
            </div>
            
            <div className="px-4 py-2 space-y-3">
              <label className="flex items-center justify-between cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg transition-colors ${settings.enableGlobalMonitor ? 'bg-amber-100 text-amber-600' : 'bg-gray-100 text-gray-400'}`}>
                    {settings.enableGlobalMonitor ? <Bell className="h-3.5 w-3.5" /> : <BellOff className="h-3.5 w-3.5" />}
                  </div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Monitor Global</span>
                </div>
                <div 
                  onClick={() => updateSettings({ enableGlobalMonitor: !settings.enableGlobalMonitor })}
                  className={`w-9 h-5 rounded-full relative transition-colors ${settings.enableGlobalMonitor ? 'bg-amber-500' : 'bg-gray-300 dark:bg-gray-600'}`}
                >
                  <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${settings.enableGlobalMonitor ? 'left-5' : 'left-1'}`} />
                </div>
              </label>

              <label className="flex items-center justify-between cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg transition-colors ${settings.enableBrowserNotifications ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-400'}`}>
                    <Activity className="h-3.5 w-3.5" />
                  </div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Desktop Push</span>
                </div>
                {!settings.enableBrowserNotifications && Notification.permission !== 'granted' ? (
                    <button 
                      onClick={requestPermissions}
                      className="text-[10px] bg-indigo-50 text-indigo-600 px-2 py-1 rounded-md font-bold hover:bg-indigo-100 transition-colors"
                    >
                      ACTIVAR
                    </button>
                ) : (
                  <div 
                    onClick={() => updateSettings({ enableBrowserNotifications: !settings.enableBrowserNotifications })}
                    className={`w-9 h-5 rounded-full relative transition-colors ${settings.enableBrowserNotifications ? 'bg-indigo-500' : 'bg-gray-300 dark:bg-gray-600'}`}
                  >
                    <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${settings.enableBrowserNotifications ? 'left-5' : 'left-1'}`} />
                  </div>
                )}
              </label>
            </div>
          </div>

          <div className="py-2 border-t border-gray-100 dark:border-gray-800">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Diagnóstico
            </div>
            
            <Link href="/exchange-logs" className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
              <Activity className="mr-3 h-5 w-5 text-gray-400 group-hover:text-emerald-500" />
              Logs Exchange
            </Link>
            
            <Link href="/api-tester" className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
              <Terminal className="mr-3 h-5 w-5 text-gray-400 group-hover:text-teal-500" />
              API Tester
            </Link>
            
            <Link href="/chase-playground" className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
              <Terminal className="mr-3 h-5 w-5 text-gray-400 group-hover:text-amber-500" />
              Chase Playground
            </Link>
          </div>

          <div className="py-2">
            <Link href="/settings" className="group flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
              <Settings className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
              Configurar Bot
            </Link>
          </div>

        </div>
      )}
    </div>
  )
}
