# Interfaz de Usuario (UI) - Representación Estructural Optimizada para IA

Este documento contiene una representación de la interfaz del **Binance Futures Tracker** en un formato denso (YAML) diseñado para ser leído eficientemente por un LLM interactuando con el proyecto. Omite clases utilitarias de CSS (como Tailwind) y se enfoca en jerarquía, funcionalidad y componentes de estado.

```yaml
app:
  # Encabezado Principal
  header:
    title: "Binance Futures Tracker"
    subtitle: "Rastrea y analiza tus operaciones en Binance Futures"

  # Panel de Controles y Filtros
  controls:
    filters:
      - select#symbol: { label: "Símbolo", value: "BTC/USDT" }
      - select#logic: { label: "Método", options: ["Atomic Match (FIFO)", "LIFO", "Quantity Match"] }
      - checkbox#unrealized: { label: "Incluir PnL Flotante (Abiertas)", checked: false }
    actions:
      - button#load_history: "Continuar previos (7 días)"
      - button#sync_binance: "Sincronizar con Binance"

  # Grid de Estadísticas (KPIs)
  stats:
    - card: { label: "Total Trades", value: "0" }
    - card: { label: "PnL Neto", value: "$0.00", status: "positive" }
    - card: { label: "Win Rate", value: "0.0%" }
    - card: { label: "PnL Promedio", value: "$0.00", status: "positive" }

  # Sección Principal de Datos
  main_content:
    - section#history:
        title: "Historial de Operaciones"
        state: "No hay operaciones registradas"
        table_schema:
          headers: ["Fecha", "Símbolo", "Lado", "Cantidad", "Precio Entra", "Precio Sale", "PnL", "Comisión", "Duración"]
    
    - section#charts:
        type: "Area/Line Chart (Recharts)"
        metrics: ["PnL Acumulado", "Puntos de Entrada/Salida"]
```

## Ejemplo Poblado: 1000PEPEUSDC (Datos Reales)

Cuando se selecciona un símbolo con actividad como `1000PEPEUSDC`, la interfaz expone componentes enriquecidos. A continuación su representación estructural:

```yaml
ui_populated_state:
  symbol_selector:
    current: "1000PEPEUSDC"
  stats_cards:
    total_trades: "28"
    pnl_neto: "$9.19"
    win_rate: "89.3%"
    pnl_promedio: "$0.33"
  chart_schema:
    component: "LineChart (Recharts)"
    axis_x: "Time/Date (format: MM/DD HH:mm + Open slots)"
    axis_y: "Price (USDT)"
    series:
      - data_key: "price"
        label: "Precio"
        type: "monotone"
        stroke: "#2563eb"
    features: "Interactive entry/exit dots on line with hover tooltips"
  trades_table:
    headers: ["Entrada", "Salida", "Cantidad", "Precio Entrada", "Precio Salida", "Duración", "PnL Neto", "PnL %"]
    row_sample_0:
      entrada: "24/03/2026 00:19:23 (BUY)"
      salida: "24/03/2026 21:11:35 (SELL)"
      cantidad: "1,471.00"
      precio_entrada: "$0.003404"
      precio_salida: "$0.003539"
      duracion: "20h 52m"
      pnl_neto: "+ $0.20"
      pnl_porcentual: "+3.94%"
```

## Notas Operativas para IA
- **Estados de Carga**: Existen estados visuales transitorios ("Sincronizando...", "Cargando...") al interactuar con acciones principales.
- **Flujo de Datos**: La tabla representa "Trades" procesados (agrupación final de operaciones de subida y bajada tras aplicar la lógica de emparejamiento seleccionada, deducidas las comisiones).
- **Interactividad**: Los identes `symbol`, `logic` y `unrealized` están vinculados directamente al estado global (probablemente React/Zustand o Context) que comanda la refacturación de datos del backend.
