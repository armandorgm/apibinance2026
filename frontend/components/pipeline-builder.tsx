"use client"

import { useEffect, useState } from "react"
import { fetchPipelines, fetchPipelineMetadata, createPipeline, togglePipeline, deletePipeline, BotPipeline, PipelineMetadata } from "@/lib/api"
import { AdaptiveChaseButton } from "./adaptive-chase-button"

export function PipelineBuilder() {
  const [pipelines, setPipelines] = useState<BotPipeline[]>([])
  const [metadata, setMetadata] = useState<PipelineMetadata | null>(null)
  const [loading, setLoading] = useState(true)

  // New Pipeline State
  const [name, setName] = useState("")
  const [symbol, setSymbol] = useState("1000PEPEUSDC")
  const [providerA, setProviderA] = useState("")
  const [operator, setOperator] = useState("")
  const [providerB, setProviderB] = useState("")
  const [offsetStr, setOffsetStr] = useState("0.0")
  const [action, setAction] = useState("")

  const loadData = async () => {
    try {
      const [pData, mData] = await Promise.all([
        fetchPipelines(),
        fetchPipelineMetadata()
      ])
      setPipelines(pData)
      setMetadata(mData)
      if (mData.providers.length > 0) {
        setProviderA(mData.providers[0])
        setProviderB(mData.providers[0])
      }
      if (mData.operators.length > 0) setOperator(mData.operators[0])
      if (mData.actions.length > 0) setAction(mData.actions[0])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const handleCreate = async () => {
    try {
      const configObj = {
        condition: {
          provider_a: providerA,
          operator: operator,
          provider_b: providerB,
          offset: parseFloat(offsetStr) || 0.0
        },
        action: {
          type: action
        }
      }
      
      await createPipeline({
        name,
        symbol,
        is_active: true,
        trigger_event: "POLLING",
        pipeline_config: JSON.stringify(configObj)
      })
      alert("Pipeline creado exitosamente")
      setName("")
      loadData()
    } catch (e: any) {
      alert(`Error: ${e.message}`)
    }
  }

  const handleToggle = async (id: number) => {
    try {
      await togglePipeline(id)
      loadData()
    } catch (e) {
      alert("Error toggling pipeline")
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deletePipeline(id)
      loadData()
    } catch (e) {
      alert("Error deleting pipeline")
    }
  }

  if (loading) return <div className="p-4">Cargando Tareas...</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-x md:divide-y-0 h-full">
      {/* Left Column: Form */}
      <div className="p-6 flex flex-col gap-5 overflow-y-auto bg-gray-50 dark:bg-gray-800/50">
        <h2 className="font-semibold text-lg text-gray-900 dark:text-white">Nueva Tarea (Pipeline)</h2>
        
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombre de la Tarea</label>
            <input 
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
              placeholder="Ej: Compra PEPE si baja" 
              value={name} 
              onChange={e => setName(e.target.value)} 
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Símbolo Base</label>
            <input 
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
              placeholder="Ej: 1000PEPEUSDC" 
              value={symbol} 
              onChange={e => setSymbol(e.target.value.toUpperCase())} 
            />
          </div>

          <div className="p-4 border rounded-md dark:border-gray-700 bg-white dark:bg-gray-900 space-y-4 shadow-sm">
            <span className="text-xs font-semibold px-2 py-1 bg-blue-100 text-blue-800 rounded dark:bg-blue-900 dark:text-blue-200">
              Bloque: Condición IF
            </span>
            
            <div className="space-y-1 mt-3">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Variable A</label>
              <select className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700" value={providerA} onChange={e => setProviderA(e.target.value)}>
                {metadata?.providers.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Operador</label>
              <select className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700" value={operator} onChange={e => setOperator(e.target.value)}>
                {metadata?.operators.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Variable B</label>
              <select className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700" value={providerB} onChange={e => setProviderB(e.target.value)}>
                {metadata?.providers.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Offset (Variable B + X)</label>
              <input 
                className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
                type="number" step="0.0001" 
                value={offsetStr} 
                onChange={e => setOffsetStr(e.target.value)} 
              />
            </div>
          </div>

          <div className="p-4 border rounded-md dark:border-gray-700 bg-white dark:bg-gray-900 space-y-4 shadow-sm">
             <span className="text-xs font-semibold px-2 py-1 bg-green-100 text-green-800 rounded dark:bg-green-900 dark:text-green-200">
               Bloque: Acción THEN
             </span>
             <div className="space-y-1 mt-3">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ejecutar</label>
              <select className="w-full px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700" value={action} onChange={e => setAction(e.target.value)}>
                {metadata?.actions.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>

          <button 
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-md disabled:bg-gray-400"
            onClick={handleCreate} 
            disabled={!name || !symbol}
          >
            Instalar Tarea en el Engine
          </button>
        </div>
      </div>

      {/* Right Column: List */}
      <div className="col-span-2 p-6 overflow-y-auto">
        <div className="flex flex-row items-center justify-between mb-4">
          <h2 className="font-semibold text-lg text-gray-900 dark:text-white">Secuencias Activas en Memoria</h2>
          <AdaptiveChaseButton symbol={symbol} />
        </div>
        
        {pipelines.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-500 border border-dashed rounded-lg dark:border-gray-700">
            <p>No hay pipelines configurados.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="lowercase tracking-wider border-b text-gray-500 dark:text-gray-400 dark:border-gray-700">
                <tr>
                  <th className="font-semibold pb-3 px-4">Estado</th>
                  <th className="font-semibold pb-3 px-4">Símbolo</th>
                  <th className="font-semibold pb-3 px-4 w-full">Regla / Estructura</th>
                  <th className="font-semibold pb-3 px-4 text-right">Admin</th>
                </tr>
              </thead>
              <tbody className="divide-y dark:divide-gray-700">
                {pipelines.map(pipe => {
                  let p = null;
                  try { p = JSON.parse(pipe.pipeline_config) } catch(e) {}
                  
                  return (
                    <tr key={pipe.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <td className="py-3 px-4">
                        {pipe.is_active ? 
                          <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold dark:bg-emerald-900/30 dark:text-emerald-400">ACTIVA</span> : 
                          <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs font-semibold dark:bg-gray-800 dark:text-gray-400 border">PAUSADA</span>
                        }
                      </td>
                      <td className="py-3 px-4 font-mono text-gray-700 dark:text-gray-300">{pipe.symbol}</td>
                      <td className="py-3 px-4">
                        <div className="flex flex-col gap-1">
                          <span className="font-semibold text-gray-900 dark:text-white">{pipe.name}</span>
                          {p && (
                            <div className="text-xs text-gray-500 dark:text-gray-400 flex gap-1 items-center flex-wrap">
                              <span className="bg-gray-100 dark:bg-gray-800 px-1 rounded">{p.condition?.provider_a}</span>
                              <span className="font-mono">{p.condition?.operator}</span>
                              <span className="bg-gray-100 dark:bg-gray-800 px-1 rounded">{p.condition?.provider_b}</span>
                              <span className="font-mono">+ {p.condition?.offset}</span>
                              <span className="mx-1">→</span>
                              <span className="border px-1 rounded bg-white dark:bg-gray-900">{p.action?.type}</span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right space-x-2">
                         <button 
                           className="p-2 border rounded-md hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700" 
                           onClick={() => handleToggle(pipe.id)}
                         >
                           {pipe.is_active ? "⏸️" : "▶️"}
                         </button>
                         <button 
                           className="p-2 border border-red-200 text-red-600 rounded-md hover:bg-red-50 dark:border-red-900 dark:hover:bg-red-900/20" 
                           onClick={() => handleDelete(pipe.id)}
                         >
                           🗑️
                         </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
