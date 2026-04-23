import type { Metadata } from 'next'
import './globals.css'
import { QueryProvider } from './providers/query-provider'
import { DeveloperHubDropdown } from '@/components/developer-hub-dropdown'
import { NotificationProvider } from '@/components/notification-provider'
import { Toaster } from 'sonner'

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
          <NotificationProvider>
            <Toaster position="bottom-right" richColors closeButton expand={true} />
            <DeveloperHubDropdown />
            {children}
          </NotificationProvider>
        </QueryProvider>
      </body>
    </html>
  )
}
