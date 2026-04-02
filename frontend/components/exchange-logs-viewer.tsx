'use client'

import { useState } from 'react'
import { ExchangeLog } from '@/lib/api'
import { format } from 'date-fns'

interface Props {
  logs: ExchangeLog[]
}

export function ExchangeLogsViewer({ logs }: Props) {
  const [selectedLog, setSelectedLog] = useState<ExchangeLog | null>(null)

  const handleRowClick = (log: ExchangeLog) => {
    setSelectedLog(selectedLog?.id === log.id ? null : log)
  }

  const formatJSON = (jsonString: string | null) => {
    if (!jsonString) return 'null'
    try {
      return JSON.stringify(JSON.parse(jsonString), null, 2)
    } catch {
      return jsonString
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Fecha / Hora</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Método</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Estado</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {logs.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No hay interacciones registradas.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <optgroup key={log.id} className="contents">
                  <tr 
                    onClick={() => handleRowClick(log)}
                    className={`cursor-pointer transition-colors ${
                      log.is_error ? 'bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30' : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {format(new Date(log.created_at), 'dd/MM/yyyy HH:mm:ss')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600 dark:text-blue-400">
                      {log.method}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {log.is_error ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100">
                          Error
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                          Éxito
                        </span>
                      )}
                    </td>
                  </tr>
                  {selectedLog?.id === log.id && (
                    <tr>
                      <td colSpan={3} className="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Parámetros (Input):</h4>
                            <pre className="bg-gray-100 dark:bg-black p-3 rounded text-xs text-green-600 dark:text-green-400 overflow-x-auto">
                              {formatJSON(log.parameters)}
                            </pre>
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                              {log.is_error ? 'Mensaje de Error:' : 'Respuesta (Output):'}
                            </h4>
                            <pre className={`p-3 rounded text-xs overflow-x-auto ${
                              log.is_error ? 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300' : 'bg-gray-100 dark:bg-black text-blue-600 dark:text-blue-400'
                            }`}>
                              {log.is_error ? log.error_message : formatJSON(log.response)}
                            </pre>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </optgroup>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
