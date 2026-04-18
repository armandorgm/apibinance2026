'use client'

import { useRef, useEffect, useState, useMemo } from 'react'
import { Trade } from '@/lib/api'
import { formatPrice } from '@/lib/utils'
import { format } from 'date-fns'

interface GuitarHeroChartProps {
  trades: Trade[]
}

export function GuitarHeroChart({ trades }: GuitarHeroChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [hoveredTrade, setHoveredTrade] = useState<Trade | null>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  const height = 4000 // Altura del canvas de scroll
  
  // Procesamiento de datos y escalas
  const { processedTrades, minPrice, maxPrice, minTime, maxTime, maxAmount } = useMemo(() => {
    if (!trades.length) return { processedTrades: [], minPrice: 0, maxPrice: 0, minTime: 0, maxTime: 0, maxAmount: 0 }

    const now = Date.now()
    let minP = Infinity
    let maxP = -Infinity
    let minT = Infinity
    let mxAmount = 0

    trades.forEach(t => {
      if (t.entry_price < minP) minP = t.entry_price
      if (t.entry_price > maxP) maxP = t.entry_price
      if (t.exit_price && t.exit_price < minP) minP = t.exit_price
      if (t.exit_price && t.exit_price > maxP) maxP = t.exit_price
      
      const entryTime = new Date(t.entry_datetime).getTime()
      if (entryTime < minT) minT = entryTime

      if (t.entry_amount > mxAmount) mxAmount = t.entry_amount
    })

    const padding = (maxP - minP) * 0.1
    minP -= padding
    maxP += padding

    // Evitamos divisiones por 0
    if (minP === maxP) {
      minP -= 10
      maxP += 10
    }
    
    // Dejar margen de 5% de tiempo al inicio
    const timeSpan = Math.max(now - minT, 1000)
    minT = minT - timeSpan * 0.05

    return { 
      processedTrades: trades, 
      minPrice: minP, 
      maxPrice: maxP, 
      minTime: minT, 
      maxTime: now,
      maxAmount: mxAmount || 1
    }
  }, [trades])

  // Desplazar al fondo al cargar (ver el "presente")
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [trades])

  // Helpers de mapeo (100% width del viewBox para SVG reactivo)
  const mapX = (price: number) => {
    return ((price - minPrice) / (maxPrice - minPrice)) * 1000
  }

  const mapY = (timestamp: number) => {
    return ((timestamp - minTime) / (maxTime - minTime)) * height
  }

  const getThickness = (amount: number) => {
    return Math.max(1.5, Math.pow(amount / maxAmount, 0.7) * 10) // Escala no lineal para el grosor
  }

  return (
    <div 
      className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar relative bg-gray-950"
      ref={containerRef}
      onMouseMove={(e) => {
        const rect = containerRef.current?.getBoundingClientRect()
        if (rect) {
          setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top })
        }
      }}
    >
      <div style={{ height: `${height}px`, width: '100%', position: 'relative' }}>
        
        {/* Marcadores de Fondo (Background Grid) */}
        <div className="absolute inset-0 pointer-events-none opacity-20">
          <div className="w-full h-full border-x border-gray-800" style={{ background: 'linear-gradient(90deg, transparent 0%, rgba(79, 70, 229, 0.05) 50%, transparent 100%)' }}></div>
        </div>

        {/* Eje de Tiempo Fijo (Izquierda) */}
        <div className="absolute left-0 top-0 bottom-0 w-20 border-r border-gray-800/50 bg-gray-950/80 backdrop-blur pointer-events-none z-10 hidden sm:block">
           {/* Generar algunos ticks de tiempo */}
           {Array.from({length: 10}).map((_, i) => {
             const yPos = (i / 10) * height
             const t = minTime + (i / 10) * (maxTime - minTime)
             return (
               <div key={i} className="absolute left-2 text-[10px] text-gray-500" style={{ top: `${yPos}px`, transform: 'translateY(-50%)' }}>
                 {format(new Date(t), 'HH:mm')}
                 <div className="w-full h-px bg-gray-800/50 absolute left-16 top-1/2" style={{ width: '100vw' }} />
               </div>
             )
           })}
        </div>

        <svg 
          className="absolute inset-0 pointer-events-none" 
          width="100%" 
          height="100%" 
          viewBox={`0 0 1000 ${height}`} 
          preserveAspectRatio="none"
        >
          <defs>
            <filter id="glow-green" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <filter id="glow-red" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <filter id="glow-blue" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Línea del Presente */}
          <line x1="0" y1={height - 2} x2="1000" y2={height - 2} stroke="#3b82f6" strokeWidth="2" filter="url(#glow-blue)" strokeDasharray="5 5" opacity="0.8" />
          <text x="50%" y={height - 10} fill="#3b82f6" fontSize="12" textAnchor="middle" className="font-mono tracking-widest opacity-80" style={{ transform: 'scaleX(0.8)' }}>
            LÍNEA TEMPORAL ACTUAL (NOW)
          </text>

          {/* Dibujar Trades */}
          {processedTrades.map((trade, idx) => {
             const t1 = new Date(trade.entry_datetime).getTime()
             const y1 = mapY(t1)
             const x1 = mapX(trade.entry_price)

             let t2 = trade.exit_datetime ? new Date(trade.exit_datetime).getTime() : maxTime
             const y2 = mapY(t2)
             const x2 = trade.exit_price !== null ? mapX(trade.exit_price) : x1

             const isOpen = !trade.exit_datetime
             const pnl = trade.pnl_net || 0
             // Las abiertas las pintamos moradas/azules, cerradas verde/rojo según PnL
             const isWin = pnl > 0
             const color = isOpen ? '#8b5cf6' : (isWin ? '#10b981' : '#ef4444')
             const filter = isOpen ? 'url(#glow-blue)' : (isWin ? 'url(#glow-green)' : 'url(#glow-red)')
             
             // Curva Bezier para la caída
             const controlY1 = y1 + (y2 - y1) * 0.5
             const controlY2 = y1 + (y2 - y1) * 0.5
             const pathD = `M ${x1} ${y1} C ${x1} ${controlY1}, ${x2} ${controlY2}, ${x2} ${y2}`

             const thickness = getThickness(trade.entry_amount)

             return (
               <g 
                 key={`trade-${trade.id}-${idx}`} 
                 className="pointer-events-auto cursor-pointer"
                 onMouseEnter={() => setHoveredTrade(trade)}
                 onMouseLeave={() => setHoveredTrade(null)}
               >
                 {/* Línea invisible gruesa para pescar el hover */}
                 <path 
                   d={pathD} 
                   fill="none" 
                   stroke="transparent" 
                   strokeWidth="30" 
                 />
                 
                 {/* Línea visible de la ruta */}
                 <path 
                   d={pathD} 
                   fill="none" 
                   stroke={color} 
                   strokeWidth={thickness} 
                   filter={filter}
                   opacity={hoveredTrade && hoveredTrade.id !== trade.id ? 0.2 : 0.9}
                   className="transition-opacity duration-300"
                 />

                 {/* Nodo Entrada */}
                 <circle cx={x1} cy={y1} r={thickness + 2} fill="#111827" stroke={color} strokeWidth="2" filter={filter} />
                 
                 {/* Nodo Salida (solo si está cerrado) */}
                 {!isOpen && (
                   <polygon 
                     points={`${x2},${y2-5} ${x2+5},${y2} ${x2},${y2+5} ${x2-5},${y2}`} 
                     fill="#111827" stroke={color} strokeWidth="2" filter={filter} 
                   />
                 )}

                 {/* Riel de luz difuminado si está abierto y continua bajando al presente */}
                 {isOpen && (
                   <circle cx={x2} cy={y2} r="4" fill="#8b5cf6" filter="url(#glow-blue)" className="animate-pulse" />
                 )}
               </g>
             )
          })}
        </svg>

        {/* Tooltip Dinámico HTML para alta fidelidad */}
        {hoveredTrade && (
          <div 
            className="fixed z-50 bg-gray-900/90 backdrop-blur-md border border-gray-700 p-4 rounded-xl shadow-2xl pointer-events-none transform -translate-x-1/2 -translate-y-[120%]"
            style={{ left: mousePos.x, top: mousePos.y }}
          >
            <div className="flex items-center justify-between gap-6 mb-2">
              <span className={`px-2 py-0.5 rounded text-xs font-black uppercase tracking-wider ${hoveredTrade.entry_side === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                {hoveredTrade.entry_side}
              </span>
              <span className="text-gray-400 text-xs font-mono">
                ID: {hoveredTrade.id}
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm font-mono mb-3">
              <div className="text-gray-400">Volumen:</div>
              <div className="text-white text-right font-bold">{hoveredTrade.entry_amount}</div>
              
              <div className="text-gray-400">Entry:</div>
              <div className="text-white text-right">{formatPrice(hoveredTrade.entry_price)}</div>
              
              <div className="text-gray-400">Exit:</div>
              <div className="text-white text-right">{hoveredTrade.exit_price ? formatPrice(hoveredTrade.exit_price) : 'OPEN'}</div>
            </div>

            <div className="border-t border-gray-800 pt-3 flex justify-between items-center">
              <span className="text-gray-400 text-xs uppercase tracking-widest font-semibold">Net PnL</span>
              <span className={`text-lg font-black ${hoveredTrade.pnl_net > 0 ? 'text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]'}`}>
                 {formatPrice(hoveredTrade.pnl_net)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
