# 🏆 VISIÓN DEL PRODUCT OWNER - apibinance2026

Este documento constituye la **declaración de visión y manifiesto estratégico** del proyecto. Define el *qué* y el *porqué* detrás de cada decisión técnica, sirviendo como la guía principal para el desarrollo de funcionalidades y la priorización de tareas.

---

## 🎯 Propuesta de Valor

**apibinance2026** no es solo una interfaz para Binance; es un **Sistema de Control de Alta Fidelidad** diseñado para traders profesionales de Binance Futures (USDⓈ-M) que exigen transparencia absoluta en su operativa.

El problema que resolvemos es la "opacidad del exchange":
1. **PnL Invisible**: Binance oculta el costo real de las comisiones y el emparejamiento histórico exacto. Nosotros lo calculamos mediante algoritmos **FIFO/LIFO/Atomic**.
2. **Órdenes Fantasma**: Las órdenes del *Algo Service* (TP/SL/Trailing) suelen ser difíciles de rastrear programáticamente. Nosotros proporcionamos **visibilidad total**.
3. **Deslizamiento (Slippage)**: El trading manual a menudo resulta en ejecuciones Taker costosas. Nosotros implementamos el **Chase Entry (Pure Maker Mode)**.

---

## 🚀 Pilares Estratégicos (Core Features)

### 1. Unified Counter-Order Engine (UCOE V5.9)
El motor central que orquesta la bi-direccionalidad del mercado. Su misión es generar contrapartidas inteligentes basadas en el historial, integrando métricas de riesgo y gestión automatizada del flag `reduceOnly`.

### 2. Chase Entry: Aggressive Maker Mode
Una política de ejecución innegociable definida por el PO:
- **Entrada**: Debe ser **Maker (Post-Only)** mediante el uso de `GTX`. El sistema "caza" el precio Bid/Ask hasta 20 veces para asegurar el llenado como creador de mercado, optimizando comisiones.
- **Salida**: Se prioriza la **Velocidad de Cierre** sobre el tipo de orden. Se utiliza `GTC` para garantizar la salida una vez alcanzado el objetivo de Profit.

### 3. Atocmity & Symmetry (Sincronización de Contratos)
El sistema garantiza que la orden de salida (Take Profit) coincida exactamente en cantidad (`z`) con lo ejecutado en la entrada. No permitimos discrepancias de contratos que dejen posiciones huérfanas.

---

## 📊 Definición de Éxito (KPIs de Producto)

- **Transparencia Total**: Cada trade visualizado en el dashboard debe ser rastreable hasta sus *Fills* individuales.
- **Resiliencia del Stream**: Datos de Bid/Ask en tiempo real con una latencia mínima y reconexión automática inteligente.
- **Seguridad en la Ejecución**: Prevención de errores críticos de la API de Binance (`-4164 MIN_NOTIONAL`, `-2010 Account has insufficient balance`).
- **Integridad de Datos**: Normalización estricta de símbolos entre el estándar CCXT y los IDs nativos de Binance.

---

## 🛑 Restricciones y Reglas de Negocio

- **Factor 1**: Todas las cantidades se manejan en unidades estándar de contratos.
- **Stop Loss Exclusion**: El algoritmo de matching ignora órdenes de protección para no ensuciar el cálculo de rentabilidad de la estrategia principal.
- **Independencia de Framework**: La lógica de negocio (Python/FastAPI) es soberana y debe poder funcionar independientemente de la UI (Next.js).

---

> [!NOTE]
> Este documento es mantenido dinámicamente. Cualquier cambio estructural en la estrategia de trading (ej: permitir entradas Taker) debe ser reflejado aquí primero.
