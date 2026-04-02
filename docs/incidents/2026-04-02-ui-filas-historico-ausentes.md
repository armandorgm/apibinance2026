# Incidente: Filas del Dashboard Desaparecidas

## Problema
Investigué el fallo crítico "dejaron de mostrarse las filas en el historial de operaciones del dashboard del frontend". Noté que el UI intentaba renderizar un array vacío o recibía un error desde el API. Al analizar nuestro backend `GET /api/trades/history`, encontré que las recientes extensiones (TP/SL/Órdenes Pendientes) tenían un problema de notación donde se asumía que el objeto de orden (`order`) de CCXT era una clase de Objeto, intentando acceder a propiedades a través del operador punto `order.info.get()`. Al ser diccionarios limpios en Python, esto gatillaba un `AttributeError: 'dict' object has no attribute 'info'` y causaba un error 500, bloqueando totalmente el endpoint. Adicionalmente, existían riesgos de llamar `.lower()` en diccionarios devolviendo valores de `side` nulos.

## Solución
Implementé un parche estructural dentro de `backend/app/api/routes.py`:
1. Reemplacé las notaciones inseguras de punto por uso seguro de utilidades dict `order.get('info', {}).get(...)`.
2. Reforcé la prevención de errores encadenados en literales transformando `order.get('side', '').lower()` a un bloque iterado blindado `(raw.get('side') or '').lower()`.
La solución está encapsulada dentro de la arquitectura actual y ha re-habilitado la sincronización histórica íntegramente. Como no hay tests que evalúen la caída del UI por el endpoint, sugerí actualizar a futuro los unit tests del historial para validar objetos mock de CCXT.

## Impacto
Lancé la actualización en vuelo, recuperando la estabilidad del Dashboard Frontend. Los usuarios ahora visualizan instantáneamente sus trades flotantes, órganas y pendientes sin que un `dict` impida la carga general.
