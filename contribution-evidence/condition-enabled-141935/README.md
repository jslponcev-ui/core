# Revisión del arreglo de condiciones enabled (#141935)

Estado: implementación terminada y subida a la rama `work/condition-enabled-141935`; todavía no se ha abierto un PR.

- Problema original: https://github.com/home-assistant/core/issues/141935
- Código completo del cambio: https://github.com/jslponcev-ui/core/commit/df284cf3303ec8fec22a4081dfb9b14a10be09ef
- Descripción preparada con la plantilla completa: [PR_DESCRIPTION.md](PR_DESCRIPTION.md)
- Base de trabajo: `a6e0e3b5ccae2bac32367389c3cd7899b8dc8f64`.
- Alcance: 2 archivos de producción y 3 de pruebas; 345 líneas añadidas y 18 eliminadas.

## Qué falla y qué cambia

Una automatización puede definir una variable de disparo como `enable_condition: true` y usar `enabled: "{{ enable_condition }}"` en una condición. Antes, Home Assistant evaluaba esa plantilla al preparar la condición, sin las variables del disparo. La condición podía quedar desactivada y permitir acciones que debería bloquear.

Ahora la condición guarda la plantilla y la evalúa cada vez que se comprueba, con las variables de esa ejecución:
1. Si enabled da falso, la condición devuelve el mismo resultado de condición desactivada que antes.
2. Si da verdadero, comprueba la condición real.
3. Si la plantilla produce un error, lo comunica como error de condición y bloquea las acciones.
4. El envoltorio conserva la suscripción a cambios, la limpieza del objeto hijo y una sola entrada de traza.

El mismo punto de entrada cubre condiciones antiguas y de plataforma. Los tests comprueban condiciones anidadas AND/OR/NOT, recargas y scripts if/choose que reutilizan condiciones entre ejecuciones.

## Decisiones que debes comprender antes de enviarlo

- Las plantillas siguen siendo limitadas (`limited=True`); esto no habilita funciones como `states()` dentro de enabled.
- Enabled se vuelve a evaluar en cada comprobación. No se almacena un resultado que pertenezca a una ejecución anterior.
- Los errores de renderizado se detectan al comprobar la condición, en lugar de durante su configuración.
- Si enabled es una plantilla, se prepara la condición hija aunque después la plantilla dé falso. Un `enabled: false` literal sigue evitando esa preparación.
- El envoltorio conserva la necesidad de sondeo, ya que el resultado de enabled puede depender de variables de ejecución.

## Comprobaciones realizadas

- Suite: **654 passed in 20.61s**.
- Comando: `PYTHONPATH=$PWD /tmp/ha-uv/bin/uv run --no-sync python -m pytest -q tests/helpers/test_condition.py tests/helpers/test_script.py tests/components/automation --disable-warnings --tb=short`.
- Prueba de regresión: las cuatro variantes state/and/or/not fallan con los dos archivos de producción originales. Después de restaurar la implementación, las cuatro pasan.
- Ruff check y Ruff format --check: pasan en los cinco archivos.
- Pylint en modo serial (`-j 1`): pasa en los cinco archivos.
- `git diff --check`: pasa.

## Limitaciones de la validación local

Se ejecutaron `script/setup` y `prek run --all-files`, pero no se logró una ejecución global limpia. Setup encontró que faltaba autoconf para compilar dtlssocket. Los procesos de mypy/Pylint del chequeo global encontraron restricciones de sockets. Un intento serial de mypy terminó con un error interno de psutil al consultar un PID del contenedor. Hassfest también tuvo problemas de dependencias/procesos durante los intentos.

El primer intento de prek marcó además yamllint por modificación de archivos durante la ejecución y mypy por un módulo duplicado generado (.py/.pyi). No se afirma que estos checks globales hayan pasado; la rama contiene únicamente los cinco cambios revisados. Los tests específicos y Pylint serial sí terminaron correctamente.

## Revisión humana pendiente

[AGENTS.md de Home Assistant](https://github.com/home-assistant/core/blob/dev/AGENTS.md) exige:
> Autonomous contributions are not accepted: a human must review, understand, and be able to explain every change before it is submitted.

Por ello se mantienen sin marcar las casillas de comprensión del código y de revisión del código generado. La rama y esta descripción están preparadas para que puedas revisar el cambio antes de abrir el PR.
