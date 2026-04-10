# GLOSARIO DE TÉRMINOS - apibinance2026

Este documento establece la nomenclatura oficial para el proyecto. Todos los componentes de software (Backend, Frontend y DB) deben alinearse con estas definiciones.

---

## 🏗️ Estructuras Fundamentales

### 1. Posición (Position)
- **Definición**: Una entidad virtual que representa el ciclo de vida de una inversión en el mercado.
- **Naturaleza**: No existe físicamente en la base de datos como una fila única, sino que es una **agrupación lógica**.
- **Composición**: Contiene **una sola orden de entrada** y **una o más órdenes de salida** (u órdenes opuestas que reducen/cierran la magnitud).
- **Control**: Estas agrupaciones son decididas dinámicamente según el modo de emparejamiento (FIFO, LIFO, ATOMIC) que el usuario elija en el frontend.

### 2. Orden (Order)
- **Definición**: Una solicitud enviada o ejecutada en el exchange (Binance) para realizar una operación de compra o venta.
- **Representación DB**: Es una abstracción concebida como la **unión (UNION)** de las órdenes Básicas y Condicionales.
- **Identificadores**: Para distinguirlas visualmente, se les asigna un prefijo:
    - **`B`**: Para Órdenes Básicas.
    - **`C`**: Para Órdenes Condicionales.
- **Cumplimiento**: Una Orden es llenada por uno o más **Fills**.

### 3. Orden Básica (Basic Order)
- **Definición**: Una versión específica de una Orden para operaciones estándar (LIMIT, MARKET).
- **Persistencia**: Tiene su propia tabla física (`basic_orders`) para almacenar datos específicos de la API (ej: `origQty`, `updateTime`).
- **ID**: ID original de Binance (almacenado crudo en DB).

### 4. Orden Condicional (Conditional Order)
- **Definición**: Una versión específica de una Orden para operaciones algorítmicas o de protección (Stop Loss, Take Profit, Trailing Stop).
- **Persistencia**: Tiene su propia tabla física (`conditional_orders`).
- **ID**: ID original de Binance Algo Service (`algoId`).

### 5. Fills
- **Definición**: Los intercambios concretados (ejecuciones) con la misión de "llenar" una Orden.
- **Equivalencia**: Corresponde a los objetos `Trade` de la API de CCXT (`fetch_my_trades`).
- **Identificación**: Tienen su propio ID único en la base de datos (`trade_id` de Binance).

---
*Última actualización: 2026-04-08 | Registrado por el Arquitecto.*
