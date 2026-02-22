## Bitácora de depuración: Error `Invalid Api-Key ID` (código 2008)

### 1. Contexto
- **Proyecto**: Binance Futures Tracker (`backend` con FastAPI + `ccxt`)
- **Endpoint**: `POST /api/sync` (botón “Sincronizar” en el frontend)
- **Error visible en frontend**:  
  `Error syncing trades: Error fetching trades from Binance: binance {"code":-2008,"msg":"Invalid Api-Key ID."}`

### 2. Causas típicas de `Invalid Api-Key ID` en Binance
- API Key escrita de forma incorrecta (caracter mal copiado, truncado o con espacios).
- API Key borrada / deshabilitada en Binance pero aún presente en `.env`.
- Tipo de clave no compatible (por ejemplo, clave para otra cuenta/entorno).
- Desajuste entre entorno **Testnet** y **Producción**:
  - `TESTNET=false` pero la key es de Testnet, o al revés.
- Restricciones de IP que no coinciden con la IP desde donde se hace la petición.

### 3. Estado actual del proyecto (verificado)
- Archivo `.env` en `backend` contiene valores para:
  - `BINANCE_API_KEY=********`
  - `BINANCE_API_SECRET=********`
- `exchange.py` usa esos valores directamente vía `ccxt.binance({...})`.
- `TESTNET` está actualmente en `false` en `.env`.

### 4. Plan de resolución (camino eficiente)
1. **Verificar entorno correcto (Testnet vs Producción)**  
   - Confirmar en Binance si la key creada es de **Mainnet** o **Testnet**.  
   - Alinear con `.env`:
     - Key de producción → `TESTNET=false`
     - Key de Testnet → `TESTNET=true`

2. **Validar la API Key en Binance**
   - Entrar a la sección de API Keys y confirmar que:
     - La key que copiaste sigue **activa** (no borrada ni expiradas las restricciones).
     - Tiene permisos de **Read** y **Futures** (solo lectura, sin retiros ni trading).

3. **Revisar copia de `BINANCE_API_KEY` y `BINANCE_API_SECRET`**
   - Comprobar que en `.env`:
     - No haya espacios antes/después.
     - No haya saltos de línea extra ni comillas.
     - La longitud coincida exactamente con la mostrada en Binance.
   - Tras cualquier cambio en `.env`, **reiniciar el backend** (`python run.py` con el venv activo).

#### 4.1. Hechos ya descartados (según confirmación del usuario)
- La API Key **no está mal copiada** en `.env`.
- `TESTNET` **no aplica** (se está usando producción).
- La API Key aparece como **válida/activa** en el panel de Binance.
- El backend **está usando** las keys nuevas (y el par Key/Secret corresponde).
- Permisos configurados: **Reading + Futures**.
- **Cuenta correcta** (no subcuenta/entorno equivocado).

#### 4.2. Si todo lo anterior es cierto, sospechosos más probables
- **Restricción de IP** activa y tu IP actual no coincide con la permitida.
- **Key borrada/invalidada por política de Binance**: en el panel de Binance, si dejas **IP “Unrestricted (Less Secure)”** y habilitas permisos adicionales (por ejemplo **Futures**), Binance advierte que la key puede ser **eliminada**. Eso termina en `-2008 Invalid Api-Key ID` aunque tú “no hayas cambiado nada” en el backend.
- **Regeneración silenciosa**: si rotaste el *secret* desde Binance después de copiarlo, la key puede seguir “existiendo” pero el secret anterior queda inválido (esto suele dar otros códigos, pero vale confirmar).

#### 4.3. Verificación mínima recomendada (sin tocar código)
1. En Binance → API Management → tu API Key:
   - Confirmar **IP access restriction**:
     - Si está en **Unrestricted**, cambiar a **Restrict access to trusted IPs only** y agregar tu IP pública actual.
   - Confirmar que la key sigue **Enabled** (no “deleted/expired/disabled”).
2. Guardar cambios y **reiniciar el backend**.
3. Reintentar “Sincronizar” y registrar resultado (mensaje exacto) aquí.

---

### 6. Cómo descartar que CGNAT sea el problema

> Objetivo: comprobar si estás detrás de **Carrier-Grade NAT (CGNAT)** y cómo afecta a la restricción por IP en Binance.

#### 6.1. Comprobar tu IP pública real
1. Desde el **navegador** en el mismo PC donde corre el backend, visitar una página que muestre tu IP pública, por ejemplo:
   - `https://ifconfig.me`
   - `https://api.ipify.org`
2. Anotar esa IP (ejemplo: `181.45.123.10`).

#### 6.2. Comparar con la IP del router
1. Entrar al **panel de administración del router** (suele ser `192.168.0.1`, `192.168.1.1`, etc.).
2. Buscar el valor de **WAN IP / Internet IP**.
3. Comparar:
   - Si la WAN IP del router es **igual** a la IP pública de las webs anteriores → **no estás en CGNAT**.
   - Si la WAN IP del router es **privada** (rangos `10.x.x.x`, `172.16–31.x.x`, `192.168.x.x` o `100.64–100.127.x.x`) y es distinta de la IP pública de las webs → probablemente **sí estás detrás de CGNAT**.

#### 6.3. Impacto sobre Binance e IP restrictions
- Si **NO estás en CGNAT**:
  - Puedes usar sin problema **“Restrict access to trusted IPs only”** en Binance con tu IP pública.
  - Si aun así obtienes `-2008`, el problema no es CGNAT.
- Si **SÍ estás en CGNAT**:
  - Tu router no ve la IP pública real (la comparte con otros clientes del ISP).
  - Para que Binance funcione con IP restringida, necesitas:
    - Que el ISP te proporcione una **IP pública propia** (fija o dinámica sin CGNAT), o
    - Salir por un **VPN/servidor** con IP fija conocida y registrar esa IP en Binance.
  - Mientras tanto, puedes usar **Unrestricted (Less Secure)** solo para desarrollo, pero teniendo en cuenta:
    - Mantener solo permisos de **Reading + Futures**.
    - Nunca habilitar retiros ni trading con una key Unrestricted.

> Nota: Estar bajo CGNAT por sí solo **no debería producir `Invalid Api-Key ID`** si la key está en modo *Unrestricted*. El problema aparece cuando se configura **Restrict to trusted IPs** con una IP que no es la pública real o cambia con frecuencia.

4. **Probar de nuevo el sync**
   - Con backend reiniciado y frontend apuntando a `http://localhost:8000`, pulsar “Sincronizar”.
   - Si el error persiste, anotar aquí el mensaje completo de backend y frontend.

5. **Solo si sigue fallando** (paso posterior)
   - Regenerar una nueva API Key en Binance siguiendo las recomendaciones del proyecto:
     - Tipo **System generated (HMAC)**.
     - Permisos: `Enable Reading` + `Enable Futures` únicamente.
   - Actualizar `.env`, reiniciar backend y repetir la prueba.

### 5. Próxima acción sugerida
- Antes de tocar código, seguir los pasos 1–3 del plan y registrar cualquier cambio de estado o nuevo mensaje de error en este archivo.

