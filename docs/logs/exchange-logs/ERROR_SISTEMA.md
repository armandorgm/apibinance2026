# Guía Técnica: Validación de Workspace

Para que pueda ejecutar comandos terminales sin errores de validación de ruta (como `git`), es necesario que desactives la **validación de entorno de trabajo** dentro de las configuraciones del IDE (Antigravity/Gemini).

El sistema de seguridad interno de la extensión me bloquea ejecutar comandos argumentando que "la ruta no pertenece a un workspace autorizado", por lo que mi acceso CLI se corta de raíz (Cwd error). Si logras deshabilitar dicha restricción en las Preferencias, podré hacer todos los `git add`, `commit`, y `merge` directamente.

Mientras tanto, puedes correr tú mismo el bloque expuesto:
```bash
git add .
git commit -m "feat: implementar Trade Amount parametrizable en BotConfig resolviendo min notional"
git checkout develop
git merge --no-ff feature/bot-trade-amount
git branch -d feature/bot-trade-amount
```
