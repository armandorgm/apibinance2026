'use client'

import { useState } from 'react'

export default function ApiTesterPage() {
  const [symbol, setSymbol] = useState('BTC/USDT')
  
  // Advanced Postman Mode States
  const [isAdvancedMode, setIsAdvancedMode] = useState(true)
  const [path, setPath] = useState('algo/futures/openOrders')
  const [apiType, setApiType] = useState('sapi')
  const [method, setMethod] = useState('GET')
  const [paramsJson, setParamsJson] = useState('{\n  "symbol": "BTCUSDT"\n}')
  
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFetch = async () => {
    try {
      setLoading(true)
      setError(null)
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      let res;
      if (!isAdvancedMode) {
        // Quick Simple Mode
        const url = new URL(`${API_BASE_URL}/api/debug/algo-orders`)
        if (symbol) url.searchParams.append('symbol', symbol)
        res = await fetch(url.toString())
      } else {
        // Advanced Postman Proxy Mode
        let parsedParams = {}
        try {
          parsedParams = JSON.parse(paramsJson)
        } catch (e) {
          throw new Error('Invalid JSON in Params (Revisa tus parámetros JSON)')
        }
        res = await fetch(`${API_BASE_URL}/api/debug/postman`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            path,
            api: apiType,
            method,
            params: parsedParams
          })
        })
      }
      
      const data = await res.json()
      setResponse(data)
    } catch (err: any) {
      setError(err.message || 'Error executing request')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-6 border-b dark:border-gray-700 pb-4">
            <div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-orange-500 to-amber-600">
                🧪 SAPI Postman Tester
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Construye y lanza llamadas CCXT crudas hacia Binance
              </p>
            </div>
            <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-900 p-1 rounded-lg">
               <button 
                className={`px-3 py-1 text-sm rounded transition-all ${!isAdvancedMode ? 'bg-white dark:bg-gray-700 shadow font-bold' : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}`}
                onClick={() => setIsAdvancedMode(false)}
               >
                 Rápido (Algo)
               </button>
               <button 
                className={`px-3 py-1 text-sm rounded transition-all ${isAdvancedMode ? 'bg-white dark:bg-gray-700 shadow font-bold' : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}`}
                onClick={() => setIsAdvancedMode(true)}
               >
                 Postman Mode
               </button>
            </div>
          </div>

          {/* Quick Mode */}
          {!isAdvancedMode && (
            <div className="flex gap-4 items-end mb-6 bg-emerald-50 dark:bg-emerald-900/10 p-4 rounded-lg border border-emerald-100 dark:border-emerald-800/30">
              <div className="flex-1">
                <label className="block text-sm font-medium text-emerald-800 dark:text-emerald-300 mb-1">
                  Símbolo (Par)
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  placeholder="Ej: BTC/USDT o vacio"
                  className="w-full px-4 py-2 border border-emerald-200 dark:border-emerald-700 bg-white dark:bg-gray-800 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 font-mono text-sm"
                />
              </div>
              <button onClick={handleFetch} disabled={loading} className="px-6 py-2 bg-emerald-600 text-white font-medium rounded-md hover:bg-emerald-700 transition disabled:opacity-50">
                {loading ? 'Consultando...' : 'Ejecutar (SAPI)'}
              </button>
            </div>
          )}

          {/* Advanced Mode */}
          {isAdvancedMode && (
            <div className="grid grid-cols-12 gap-4 mb-6">
              <div className="col-span-12 md:col-span-2">
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Method</label>
                <select 
                  value={method} 
                  onChange={e => setMethod(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-sm font-bold text-orange-600 dark:text-orange-400"
                >
                  <option>GET</option>
                  <option>POST</option>
                  <option>DELETE</option>
                  <option>PUT</option>
                </select>
              </div>

              <div className="col-span-12 md:col-span-3">
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">API Type (Namespace)</label>
                <select 
                  value={apiType} 
                  onChange={e => setApiType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-sm"
                >
                  <option value="sapi">sapi (e.g. /algo/futures)</option>
                  <option value="v3">v3 (Spot)</option>
                  <option value="fapiPrivate">fapiPrivate (Futures Base)</option>
                  <option value="fapiPublic">fapiPublic (Futures Mkt)</option>
                  <option value="sapiV1">sapiV1</option>
                  <option value="private">private</option>
                  <option value="public">public</option>
                </select>
              </div>

              <div className="col-span-12 md:col-span-7">
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Endpoint Path</label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 border border-r-0 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-gray-500 rounded-l text-sm font-mono">
                    /
                  </span>
                  <input
                    type="text"
                    value={path}
                    onChange={e => setPath(e.target.value)}
                    placeholder="algo/futures/openOrders"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-r bg-white dark:bg-gray-700 font-mono text-sm"
                  />
                </div>
              </div>

              <div className="col-span-12">
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex justify-between">
                  <span>Params (JSON)</span>
                  <span className="text-gray-400 font-normal">Sugerencia: {"{ \"symbol\": \"BTCUSDT\" }"}</span>
                </label>
                <textarea
                  value={paramsJson}
                  onChange={e => setParamsJson(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-orange-500 focus:border-orange-500 bg-gray-50 dark:bg-black font-mono text-sm text-green-600 dark:text-green-400"
                  spellCheck="false"
                />
              </div>

              <div className="col-span-12 flex justify-end">
                <button
                  onClick={handleFetch}
                  disabled={loading}
                  className="px-8 py-3 bg-orange-600 text-white font-bold rounded-md hover:bg-orange-700 transition disabled:opacity-50 shadow-md flex gap-2 items-center"
                >
                  {loading ? '⌛ Enviando...' : '🚀 Send Request'}
                </button>
              </div>
            </div>
          )}

          <div className="mt-8 border dark:border-gray-700 rounded-lg overflow-hidden bg-[#1e1e1e]">
            <div className="bg-[#2d2d2d] px-4 py-2 flex justify-between items-center border-b border-[#3d3d3d]">
              <span className="text-xs font-semibold uppercase text-gray-300">
                Respuesta Cruda (Raw)
              </span>
              {response && (
                <span className={`text-xs px-2 py-1 rounded font-bold ${response.status?.includes('error') ? 'bg-red-900/50 text-red-400' : 'bg-green-900/50 text-green-400'}`}>
                  {response.status}
                </span>
              )}
            </div>
            <div className="p-4 overflow-x-auto min-h-[300px]">
              {error && (
                <div className="text-red-400 font-medium mb-4 bg-red-900/20 p-3 rounded border border-red-900/50">
                  {error}
                </div>
              )}
              <pre className="text-sm font-mono text-[#d4d4d4]">
                {response ? JSON.stringify(response, null, 2) : <span className="text-gray-500 italic">// Respuesta aparecerá aquí tras presionar Send Request</span>}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
