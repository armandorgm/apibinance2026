'use client'

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { toast } from 'sonner'
import { Bell, BellOff, Info, AlertTriangle, CheckCircle2 } from 'lucide-react'

interface NotificationSettings {
  enableGlobalMonitor: boolean
  enableBrowserNotifications: boolean
}

interface NotificationContextType {
  settings: NotificationSettings
  updateSettings: (newSettings: Partial<NotificationSettings>) => void
  connectionStatus: 'connected' | 'disconnected' | 'connecting'
  requestPermissions: () => Promise<boolean>
  prices: Record<string, { bid?: number, ask?: number, last?: number }>
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<NotificationSettings>({
    enableGlobalMonitor: true,
    enableBrowserNotifications: false
  })
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected')
  const [prices, setPrices] = useState<Record<string, { bid?: number, ask?: number, last?: number }>>({})

  // Initialize settings from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('bot_notification_settings')
    if (saved) {
      try {
        setSettings(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to parse settings", e)
      }
    }
  }, [])

  const updateSettings = (newSettings: Partial<NotificationSettings>) => {
    const updated = { ...settings, ...newSettings }
    setSettings(updated)
    localStorage.setItem('bot_notification_settings', JSON.stringify(updated))
    
    if (newSettings.enableGlobalMonitor === true) {
      toast.info("Monitoreo Global Activado")
    } else if (newSettings.enableGlobalMonitor === false) {
      toast.warning("Monitoreo Global Desactivado")
    }
  }

  const requestPermissions = async () => {
    if (!("Notification" in window)) {
      toast.error("Este navegador no soporta notificaciones de escritorio")
      return false
    }

    const permission = await Notification.requestPermission()
    const granted = permission === 'granted'
    
    if (granted) {
      updateSettings({ enableBrowserNotifications: true })
      toast.success("Notificaciones de escritorio activadas")
      new Notification("Binance Tracker", {
        body: "Las notificaciones de escritorio están activas",
        icon: "/favicon.ico"
      })
    } else {
      updateSettings({ enableBrowserNotifications: false })
      toast.error("Permisos de notificación denegados")
    }
    
    return granted
  }

  const handleOrderUpdate = useCallback((data: any) => {
    if (!settings.enableGlobalMonitor) return

    const { symbol, status } = data
    const title = `Orden ${status.toUpperCase()}: ${symbol}`
    const body = `Estado actualizado a ${status}`

    // Toast Notification
    if (status === 'closed' || status === 'filled') {
      toast.success(title, {
        description: body,
        icon: <CheckCircle2 className="h-5 w-5 text-green-500" />,
        duration: 5000
      })
    } else if (status === 'canceled') {
      toast.info(title, {
        description: body,
        icon: <Info className="h-5 w-5 text-blue-500" />,
      })
    } else {
      toast.warning(title, {
        description: body,
        icon: <AlertTriangle className="h-5 w-5 text-amber-500" />,
      })
    }

    // Browser Notification
    if (settings.enableBrowserNotifications && Notification.permission === 'granted') {
      new Notification(title, { body, icon: "/favicon.ico" })
    }
  }, [settings])

  const handleTickerUpdate = useCallback((data: any) => {
    const { symbol, raw_symbol, bid, ask, last } = data
    setPrices(prev => ({
      ...prev,
      [symbol]: { bid, ask, last },
      ...(raw_symbol ? { [raw_symbol]: { bid, ask, last } } : {})
    }))
  }, [])

  // WebSocket Logic
  useEffect(() => {
    let socket: WebSocket | null = null
    let reconnectTimeout: NodeJS.Timeout
    let heartbeatInterval: NodeJS.Timeout
    let reconnectAttempts = 0
    const MAX_RECONNECT_ATTEMPTS = 10

    const connect = () => {
      if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error("[WS] Max reconnection attempts reached. Please refresh.")
        setConnectionStatus('disconnected')
        return
      }

      setConnectionStatus('connecting')
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `${protocol}//${window.location.hostname}:8000/ws/notifications`
      
      console.log(`[WS] Connecting to ${wsUrl}... (Attempt ${reconnectAttempts + 1})`)
      socket = new WebSocket(wsUrl)

      socket.onopen = () => {
        setConnectionStatus('connected')
        reconnectAttempts = 0
        console.log("[WS] Connected to notifications")
        
        // Setup heartbeat ping every 30s
        heartbeatInterval = setInterval(() => {
          if (socket?.readyState === WebSocket.OPEN) {
            socket.send("ping")
          }
        }, 30000)
      }

      socket.onmessage = (event) => {
        if (event.data === 'pong') return // Ignore pongs
        try {
          const payload = JSON.parse(event.data)
          if (payload.type === 'order_update') {
            console.log(`[WS] Order Update (${payload.data.symbol}): ${payload.data.status}`)
            handleOrderUpdate(payload.data)
          } else if (payload.type === 'ticker_update') {
            handleTickerUpdate(payload.data)
          } else if (payload.type === 'connection_established') {
            console.log(`[WS] Server ready (ID: ${payload.connection_id})`)
          }
        } catch (e) {
          // If message is just a string (like a heartbeat from server)
          if (typeof event.data === 'string' && event.data !== 'pong') {
             // console.log("[WS] Server message:", event.data)
          }
        }
      }

      socket.onclose = () => {
        setConnectionStatus('disconnected')
        clearInterval(heartbeatInterval)
        
        if (reconnectAttempts >= 10) {
          console.warn('[WS] Max reconnection attempts reached. Sleeping for 15s before reset...')
          reconnectTimeout = setTimeout(() => {
            reconnectAttempts = 0
            connect()
          }, 15000)
          return
        }

        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
        console.log(`[WS] Disconnected, retrying in ${delay/1000}s... (Attempts: ${reconnectAttempts + 1}/10)`)
        reconnectAttempts++
        reconnectTimeout = setTimeout(connect, delay)
      }

      socket.onerror = (err) => {
        console.error("[WS] Socket error", err)
        socket?.close()
      }
    }

    connect()

    return () => {
      socket?.close()
      clearTimeout(reconnectTimeout)
      clearInterval(heartbeatInterval)
    }
  }, [handleOrderUpdate, handleTickerUpdate])

  return (
    <NotificationContext.Provider value={{ settings, updateSettings, connectionStatus, requestPermissions, prices }}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}
