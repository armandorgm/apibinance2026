REGLAS DE EJECUCIÓN, DOCUMENTACIÓN Y CALIDAD TÉCNICA (ANTIGRAVITY IDE)
1. CICLO DE VIDA DEL PLAN DE EJECUCIÓN (Carpeta .temp/)
Todo procedimiento realizado por el agente IA debe seguir una trazabilidad obligatoria y en tiempo real dentro de la carpeta .temp/ del proyecto.

FASE INICIAL (Antes): Generar PLAN_EJECUCION.md detallando la hoja de ruta y los objetivos.

FASE DE PROGRESO (Durante): Actualizar el archivo con logs de cambios, errores interceptados y ajustes de estrategia.

FASE DE CIERRE (Final): Registrar el estado final del sistema.

SOBERANÍA DEL USUARIO: Al terminar, el agente NO eliminará registros. Preguntará al usuario si desea:
a) Eliminar temporales.
b) Ejecutar Plan Reparador (corregir fallos).
c) Ejecutar Plan Modificador (ajustar la solución).
d) Ejecutar Plan Restaurador (revertir al último paso estable).

2. CONMUTACIÓN DE CONTEXTO Y GESTIÓN DE BRANCHES
Si un nuevo plan o requerimiento no corresponde a la rama (branch) actual de Git:

REGISTRO DE POSTERGACIÓN: Antes de cambiar de contexto, el agente debe actualizar el PLAN_EJECUCION.md actual con el estado "POSTERGADO", detallando qué falta por hacer.

STASH DE SEGURIDAD: Realizar un git stash de los cambios actuales y registrar el puntero o nombre del stash en el documento del plan postergado para retomar después.

GESTIÓN DE BRANCH: Buscar una rama existente para el nuevo plan; si no existe, crear una nueva con nomenclatura clara.

3. GESTIÓN DE LATENCIA Y RECONSTRUCCIÓN (API LOCAL)
El agente debe ser consciente de que los cambios en el código no son instantáneos en el runtime.

ESPERA PRUDENCIAL: Tras realizar modificaciones en una API local, el agente debe esperar un tiempo razonable (5-10 segundos) antes de intentar ejecutar o testear el endpoint.

MANEJO DE ERRORES FALSOS: Si se recibe un error de conexión o 500 inmediatamente después de un cambio, el agente debe reintentar la operación tras una breve pausa adicional antes de reportar un fallo.

4. ESTÁNDARES DE IMPLEMENTACIÓN Y TESTING
Cada nueva funcionalidad o corrección debe cumplir con los siguientes criterios de calidad:

TESTING OBLIGATORIO: No se considera una tarea "finalizada" sin sus correspondientes tests (unitarios o de integración). Organizar en carpetas espejo (ej: src/auth -> tests/auth).

PRINCIPIOS SOLID: - S (Responsabilidad Única): Separar lógica de negocio de persistencia/UI.

O/P (Abierto/Cerrado): Priorizar extensión mediante interfaces.

D (Inversión de Dependencias): Inyectar dependencias para facilitar Mocks/Stubs.

CRITERIO DE SIMPLICIDAD: Si SOLID genera sobreingeniería innecesaria, priorizar código limpio y mantenible (YAGNI).

5. REGISTRO PERMANENTE DE INCIDENTES
Una vez validada la solución y cerrados los temporales, se genera el reporte en docs/incidents/:

Nomenclatura: YYYY-MM-DD-descripcion-breve.md.

Estructura: Problema, Solución (incluyendo mención a tests) e Impacto.

Lenguaje: Usar Verbos de Propiedad (Lideré, Diseñé, Implementé, Lancé).

6. PROTOCOLO DE SALIDA
Al finalizar, el agente debe emitir:
"El ciclo de ejecución ha concluido. Logs en .temp/ y reporte en docs/incidents/. Se ha gestionado el estado de ramas y stashes según la necesidad del plan. ¿Deseas eliminar los temporales o aplicar un plan reparador/modificador/restaurador?"