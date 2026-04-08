# ESTÁNDARES Y REGLAS DEL PROYECTO (VERSION UNIFICADA)

Este documento es la **Fuente de Verdad Maestra** para el desarrollo, documentación y calidad técnica. Todos los agentes y colaboradores deben seguir estas reglas sin excepción.

---

## 🚀 1. Ciclo de Vida de Ejecución (.temp/)
Toda tarea compleja debe seguir una trazabilidad obligatoria dentro de la carpeta `.temp/`:
1. **Fase Inicial**: Generar `PLAN_EJECUCION.md` detallando la hoja de ruta y objetivos.
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

## 🛠️ 6. CLI y Sintaxis (Entorno Windows/PowerShell)
Para evitar fallos de ejecución en este entorno específico:
1. **Separadores**: Usar `;` en lugar de `&&` para concatenar comandos (PowerShell nativo).
2. **Quoting en Python**: Para comandos `python -c`, usar comillas dobles `"` para el bloque de código y comillas simples `'` internas, o viceversa, asegurando que PowerShell no interpole variables inesperadas.
3. **Paths**: Siempre usar `\` para rutas locales y preferir rutas absolutas o relativas al root mediante `Cwd`.
4. **Logs**: Para monitoreo en tiempo real, usar `Get-Content <file> -Wait` (equivalente a `tail -f`).

---

> [!IMPORTANT]
> El incumplimiento de estas reglas, especialmente la de **no perder conocimiento** en `PROJECT_MAP.md`, se considera un fallo crítico de ejecución.
