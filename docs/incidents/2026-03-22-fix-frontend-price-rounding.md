# Incidente: Precios de Entrada y Salida se muestran como 0 en el Frontend

## Problema
Los usuarios reportaron que en la tabla de operaciones del Dashboard, los campos **"Precio Entrada"** y **"Precio Salida"** se mostraban siempre como `0.00`, a pesar de que los precios en Binance y en la base de datos eran correctos.

## Investigación
1. Se verificó la base de datos (`fills` y `trades`) y se confirmó que los precios almacenados eran correctos (ej: `0.0033594` para `1000PEPE`).
2. Se revisó el frontend y se identificó que todos los precios se formateaban usando `.toFixed(2)` de Javascript.
3. Para tokens con precios muy bajos (memecoins como PEPE), dos decimales no son suficientes, lo que resulta en un redondeo a `0.00`.

## Solución
1. **Diseñé** e **Implementé** un conjunto de utilidades de formateo en `frontend/lib/utils.ts`.
2. **Creé** la función `formatPrice` que ajusta automáticamente la precisión decimal según el valor del precio:
   - Valor < 0.1: 4 decimales.
   - Valor < 0.01: 6 decimales.
   - Valor < 0.0001: 8 decimales.
3. **Actualicé** los componentes `TradeTable`, `TradeChart` y la página principal para usar estas nuevas utilidades.
4. **Lancé** las correcciones verificando que el tooltip del gráfico y las tarjetas de estadísticas también utilicen el formateo dinámico.

## Impacto
Los precios de tokens de bajo valor ahora se muestran correctamente con la precisión necesaria, eliminando la confusión del usuario y permitiendo un rastreo preciso de las operaciones de alta volatilidad y bajo precio nominal.

## Tests y Validación
- Verificación manual de la salida del backend comparada con el renderizado del frontend.
- Corrección de errores de tipado en TypeScript para manejar valores nulos en el gráfico.
