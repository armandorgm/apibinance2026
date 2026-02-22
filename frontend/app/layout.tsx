import type { Metadata } from 'next'
import './globals.css'
import { QueryProvider } from './providers/query-provider'

export const metadata: Metadata = {
  title: 'Binance Futures Tracker',
  description: 'Track and analyze your Binance Futures trades',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  )
}
