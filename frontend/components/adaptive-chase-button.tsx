"use client"

import { useState } from "react"
import { triggerManualAction } from "@/lib/api"

interface AdaptiveChaseButtonProps {
  symbol: string
}

export function AdaptiveChaseButton({ symbol }: AdaptiveChaseButtonProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleTrigger = async () => {
    setIsLoading(true)
    try {
      const res = await triggerManualAction(symbol, "ADAPTIVE_OTO")
      alert(`✅ Chase Started: ${res.message}`)
    } catch (error: any) {
      alert(`❌ Error starting chase: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <button
      onClick={handleTrigger}
      disabled={isLoading || !symbol}
      className={`relative inline-flex h-10 items-center justify-center overflow-hidden rounded-md bg-zinc-950 px-6 font-medium text-emerald-400 border border-emerald-500/30 shadow-[0_0_15px_rgba(52,211,153,0.1)] transition-all hover:bg-zinc-900 hover:shadow-[0_0_20px_rgba(52,211,153,0.2)] focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 focus:ring-offset-zinc-950 disabled:opacity-50 disabled:cursor-not-allowed ${
        isLoading ? "animate-pulse" : ""
      }`}
    >
      <div className="absolute inset-0 flex h-full w-full justify-center [transform:skew(-12deg)_translateX(-100%)] group-hover:duration-1000 group-hover:[transform:skew(-12deg)_translateX(100%)]">
        <div className="relative h-full w-8 bg-white/10" />
      </div>
      <span className="mr-2">⚡</span>
      {isLoading ? "Enlazando..." : "Scalp Automático (OTO)"}
    </button>
  )
}
