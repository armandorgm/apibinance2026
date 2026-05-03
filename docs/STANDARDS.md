# ESTÁNDARES Y REGLAS DEL PROYECTO (VERSION UNIFICADA)

Este documento es la **Fuente de Verdad Maestra** para el desarrollo, documentación y calidad técnica. Todos los agentes y colaboradores deben seguir estas reglas sin excepción.

---

## 🚀 1. Ciclo de Vida de Ejecución (.temp/)
Toda tarea compleja debe seguir una trazabilidad obligatoria dentro de la carpeta `.temp/`:
1. **Fase Inicial**: Generar `PLAN_EJECUCION.md` detallando la hoja de ruta y objetivos. **CRÍTICO:** Debe incluir obligatoriamente el ID de Conversación o enlace del agente en el encabezado para evitar que agentes en paralelo sobrescriban los planes.
2. **Fase de Progreso**: Actualizar el archivo con logs de cambios, errores interceptados y ajustes.
3. **Fase de Cierre**: Registrar el estado final del sistema.
4. **Soberanía del Usuario**: Al terminar, preguntar si se desea eliminar temporales, ejecutar plan reparador, modificador o restaurador.

## 🌿 2. Gestión de Branches y Contexto
1. **No trabajar en `develop`**: Toda corrección o feature debe ir en su propia rama (`feature/name` o `hotfix/name`).
2. **Stash de Seguridad**: Antes de cambiar de contexto, realizar `git stash` y registrar el puntero en `PLAN_EJECUCION.md`.
3. **Merging**: Seguir el workflow de GitFlow (merge `--no-ff` hacia `develop` al finalizar).

## 🗺️ 3. Regla de Oro: PROJECT_MAP.md
El archivo `docs/PROJECT_MAP.md` es el "Cerebro Colectivo" del proyecto y debe protegerse:
1. **Actualización Obligatoria**: Debe actualizarse al modificar módulos, responsabilidades o flujos de datos.
2. **Incrementalidad Estricta**: Si un cambio invalida algo existente, se actualiza o borra *solo esa sección específica*.
3. **Persistencia de Conocimiento**: **JAMÁS** borrar secciones que no han sido tocadas por la tarea actual. El conocimiento almacenado debe preservarse para futuros agentes y sesiones. No se debe perder el histórico de aprendizaje del sistema.

## 📁 4. Registro de Incidentes (docs/incidents/)
1. **Centralización**: No generar archivos de procedimiento dispersos en la raíz.
2. **Consolidación**: Al completar una solución, generar UN solo reporte con: Problema, Solución e Impacto.
3. **Nomenclatura**: `YYYY-MM-DD-descripcion-breve.md`.
4. **Lenguaje**: Usar verbos de propiedad (Diseñé, Implementé, Corregí).

## 🛠️ 5. Estándares Técnicos
### Frontend (Next.js/TS)
- **Formateo**: Usar `formatPrice`, `formatAmount` y `formatPercentage` de `@/lib/utils`. Nunca usar `.toFixed()` ad-hoc.
- **Tipado**: Mantener tipado estricto en TypeScript.
### Backend (FastAPI/Python)
- **Lógica**: Respetar el principio de "Buy before Sell" y coincidencia exacta de cantidades.
- **PnL**: El cálculo neto debe descontar siempre todas las comisiones.
- **Latencia**: Al modificar la API local, esperar 5-10 segundos antes de ejecutar tests para permitir el reload del runtime.

## 🛠️ 6. CLI y Sintaxis (Entorno Preferido: Git Bash)
Para garantizar la máxima precisión y compatibilidad con agentes de IA, el entorno de ejecución estándar es **Git Bash**.

1. **Operadores de Cadena**: Usar `&&` para encadenar comandos exitosos y `||` para manejo de errores (Estándar POSIX).
2. **Paths**: Siempre usar barras diagonales `/` para rutas (ej: `backend/app/main.py`), incluso en Windows, ya que Git Bash las traduce correctamente. evitar la contra-barra `\` para prevenir errores de escape.
3. **Quoting**: Usar comillas simples `'` para strings literales y comillas dobles `"` cuando se requiera interpolación de variables.
4. **Herramientas**: Aprovechar las utilidades estándar de Bash (`grep`, `find`, `sed`, `awk`) para manipulación de archivos y logs.
5. **Logs**: Usar `tail -f <file>` para monitoreo en tiempo real.
5. **Tip de Productividad (Resiliencia)**: Si necesitas encadenar comandos en cualquier versión de PowerShell garantizando el éxito del anterior, usa:
   `command1; if ($?) { command2 }`
   Donde `$?` es una variable booleana que indica el éxito de la última ejecución.

---

> [!IMPORTANT]
> El incumplimiento de estas reglas, especialmente la de **no perder conocimiento** en `PROJECT_MAP.md`, se considera un fallo crítico de ejecución.

## 🧪 7. Verificación Previa de Servicios (Preflight Check)
Antes de ejecutar cualquier prueba técnica o de integración, es **OBLIGATORIO** verificar que tanto el frontend como el backend estén en estado `RUNNING`.

1. **Procedimiento Automático**: Ejecutar el script de verificación:
   ```powershell
   & 'f:/apibinance2026/.venv/Scripts/python.exe' scripts/preflight_check.py
   ```
2. **Criterio de Aceptación**: Si el script falla, el agente o desarrollador NO debe proceder con las pruebas hasta que los servicios sean reiniciados.

## 🧪 8. Ejecución de Pruebas Unificadas
Para garantizar que las pruebas se ejecuten con todas las dependencias necesarias (`pytest`, `sqlmodel`, etc.), es **obligatorio** utilizar el intérprete del entorno virtual (`.venv`).

### ❌ Forma INCORRECTA (Usa el Python del sistema, faltarán módulos):
```bash
python backend/tests/run_all.py
```

### ✅ Forma CORRECTA (PowerShell - Asegura el uso del .venv):
```powershell
& 'f:/apibinance2026/.venv/Scripts/python.exe' backend/tests/run_all.py
```

---
*Última actualización: 2026-04-08 | Integración de Expandable Trades funcional.*
