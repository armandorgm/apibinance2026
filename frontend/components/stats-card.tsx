'use client'

interface StatsCardProps {
  title: string
  value: string
  icon?: string
  valueColor?: string
}

export function StatsCard({ title, value, icon, valueColor = 'text-gray-900 dark:text-white' }: StatsCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className={`text-2xl font-bold mt-2 ${valueColor}`}>{value}</p>
        </div>
        {icon && (
          <div className="text-4xl opacity-20">
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}
