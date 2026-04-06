import { PipelineBuilder } from "@/components/pipeline-builder"

export default function PipelinesPage() {
  return (
    <div className="flex flex-col h-full overflow-hidden p-6 gap-6 max-w-7xl mx-auto">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Pipelines & Task Scheduler</h1>
        <p className="text-muted-foreground">
          Diseña bots secuenciales (pipelines) definiendo eventos desencadenantes, operadores analíticos, indicadores financieros y su correspondiente acción de sistema.
        </p>
      </div>
      
      <div className="flex-1 overflow-auto rounded-lg border bg-card text-card-foreground shadow-sm">
        <PipelineBuilder />
      </div>
    </div>
  )
}
