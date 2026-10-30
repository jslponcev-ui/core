# Revisión: recargas de automatizaciones que se cancelan a sí mismas

Problema: https://github.com/home-assistant/core/issues/178593
Código: https://github.com/jslponcev-ui/core/commit/3b5ab3f413a4bbca365f0fb7bfb588700b5fe768
Base: 3f8efe14b2bec286e44f0bf7769567844ad806c4
Rama para el PR: work/automation-reload-178593
Título propuesto: Prevent calling automations from cancelling their own reload

## Qué cambia

Cuando una automatización ejecuta automation.reload y su configuración ha cambiado, Home Assistant elimina la entidad anterior. Esa eliminación detiene su script, que a su vez cancela la llamada al servicio. Antes, esa cancelación interrumpía la recarga antes de añadir las entidades nuevas.

El servicio ahora ejecuta el helper de recarga en una tarea registrada en Home Assistant y la protege con asyncio.shield. El script original puede detenerse, mientras la recarga termina. La protección abarca todo el helper para conservar el bloqueo que ordena las recargas. Los permisos de administrador se comprueban antes de llegar a esta tarea. Las llamadas normales siguen esperando el resultado; no se suprimen excepciones.

## Qué demuestran las pruebas

- Recarga completa iniciada por la propia automatización modificada.
- Recarga individual iniciada por la propia automatización modificada.
- La entidad nueva queda activa, usa la configuración actualizada y puede ejecutarse.
- Otra automatización continúa funcionando.
- Cancelar al solicitante no libera antes de tiempo la coordinación entre recargas; una segunda recarga espera.
- Los tres casos fallan en la base original y pasan con el arreglo.
- 693 pruebas de automatizaciones, scripts, editor, WebSocket y helpers pasan.

Es un cambio acotado de concurrencia. No necesita hardware ni una nueva versión de una biblioteca externa. No implica que los mantenedores vayan a aceptarlo.

## Validación y límites

Ruff, formato, Pylint y mypy del cambio pasan. El chequeo global prek fue ejecutado; sus modos paralelos de Pylint/mypy/hassfest encontraron restricciones del entorno. Pylint y mypy se verificaron en modo secuencial. script/setup fue intentado, pero la instalación de todas las integraciones se detuvo por autoconf ausente para DTLSSocket. Se instalaron los requisitos de desarrollo y la dependencia cloud actual para ejecutar la batería relevante. Ver VALIDATION.md.

No se ha abierto todavía un PR ni publicado comentarios. La descripción conserva la plantilla completa. La casilla de comprensión/revisión humana queda pendiente, conforme a AGENTS.md y AI_POLICY.md.
