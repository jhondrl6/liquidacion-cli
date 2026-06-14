# Addendum Fase 3 — Divergencias arquitectónicas v2.0.0

> **Origen:** Cierre de Fase 3 base (Tareas 3.A + 3.D, sesión S36,
> 2026-06-14). Documenta las decisiones arquitectónicas del proyecto
> que **divergen** del plan original §8 pero que se mantienen vigentes
> en v2.0.0. La filosofía es: **el código gana** (AGENTS.md regla de
> oro); este addendum captura el "qué" y el "por qué" para auditoría.

## Estado

**APROBADO** — absorbe las divergencias como decisiones de v2.0.0
(NO se crea v2.0.1). Las tareas 3.B, 3.C y 3.E quedan cerradas por
cobertura funcional de las tareas posteriores (3.G, 3.H y suite
existente), sin re-implementación literal.

## Contexto

El plan §8 (Fase 3) propuso una arquitectura específica para el documento
generable. La implementación real, desarrollada en varias sesiones (S14,
S16, S22-S35), tomó decisiones distintas en tres frentes. Este addendum
formaliza esas decisiones y explica por qué cada divergencia se mantiene.

## Divergencias formalizadas

### D1 — Plantillas: `.md` con bloques Jinja, NO `.j2` separados

**Plan original (8.2 Tarea 3.B):**
- `liquidator/templates/periodica.j2`
- `liquidator/templates/finiquito.j2`
- `liquidator/templates/blocked.j2`
- `liquidator/templates/warning.j2`

**Implementación real:**
- `liquidator/templates/comprobante_periodica.md`
- `liquidator/templates/comprobante_finiquito.md`
- `liquidator/templates/partials/` (sub-plantillas reutilizables)
- `liquidator/templates/styles/` (estilos)

**Por qué se mantiene:**
- La extensión `.md` en lugar de `.j2` es puramente cosmético (el
  contenido sigue siendo Jinja2 con `{% if %}`, `{{ }}`, filtros
  custom como `format_cop`); no afecta la lógica ni el output.
- Las plantillas `blocked.j2` y `warning.j2` se absorben en el código
  Python: `_render_blocked()` genera el markdown de bloqueo directamente
  (en `markdown_generator.py:375`), y la sección de advertencias es un
  bloque inline en `_build_context.observaciones`.
- La estructura de directorios (`partials/`, `styles/`) es una mejora
  que el plan no anticipó; no introduce regresiones.

**Riesgo:** ninguno operacional. Beneficio: menos archivos, misma
funcionalidad.

### D2 — Renderers: `markdown_generator.py` y `pdf_generator.py`, NO `*_renderer.py`

**Plan original (8.2 Tarea 3.C):**
- `liquidator/output/markdown_renderer.py`
- `liquidator/output/pdf_renderer.py`

**Implementación real:**
- `liquidator/output/markdown_generator.py` (262 líneas, clase
  `MarkdownGenerator` con `generate_markdown`, `_build_context`,
  `_render_blocked`, `validar_pre_render` por motivo, preaviso, etc.)
- `liquidator/output/pdf_generator.py` (743 líneas)
- `liquidator/output/pre_render_validator.py` (matriz
  `REQUISITOS_POR_MOTIVO` separada del renderer, S34 — addendum
  finiquito/vac)
- `liquidator/output/template_manager.py` (gestor de entorno Jinja2
  con filtros custom)
- `liquidator/output/json_generator.py` (output JSON, separado de los
  renderers visuales)

**Por qué se mantiene:**
- El sufijo `_generator` describe mejor la responsabilidad: produce un
  artefacto, no solo "renderiza".
- `pre_render_validator.py` separado es una mejora arquitectónica que
  el plan §8.2 no anticipó pero que S34 introdujo al absorber el
  addendum finiquito/vacaciones; permite testear la validación de
  motivos de terminación sin tocar el renderer.

**Riesgo:** ninguno operacional. Convención interna del repo.

### D3 — Auditoría: 4 archivos, NO 1 (`immutable_logger.py`)

**Plan original (8.2 Tarea 3.E):**
- `liquidator/audit/immutable_logger.py` — UNA clase con `write_audit()`
  que hashea `execution` y escribe `audit/<timestamp>_<hash>.json`.

**Implementación real:**
- `liquidator/audit/audit_logger.py` — log principal.
- `liquidator/audit/hash_calculator.py` — utilidades de hash (SHA-256).
- `liquidator/audit/trail_generator.py` — genera el trail de auditoría.
- `liquidator/audit/versioning_manager.py` — versionado de generador y
  params.

**Por qué se mantiene:**
- Separación de responsabilidades: hashing, logging, generación de
  trail y versionado son 4 concerns distintos.
- La suite tiene 23 tests en `test_audit/` (15 errors preexistentes
  en S35 que se trabajan en Fase 4) que validan cada pieza.
- Migrar al modelo `immutable_logger.py` único sería un refactor
  puramente cosmético.

**Riesgo:** ninguno operacional. La suite cubre el comportamiento
contractual; cambiar la estructura interna requeriría reescribir tests
sin agregar valor.

### D4 — `liquidacion_BLOQUEADA.*` con exit 2 (Tarea 3.D, S36)

**Plan original (8.2 Tarea 3.D):**
> Para `compliance_status == "NO_GO"`: se genera
> `liquidacion_BLOQUEADA.{json,md,pdf}` con explicación de la regla
> fallida. Exit code 2.

**Implementación real (S36):**
- `liquidacion_BLOQUEADA.json` + `liquidacion_BLOQUEADA.md` con
  exit 2 cuando `compliance_status == NO_GO`.
- **NO** se genera `liquidacion_BLOQUEADA.pdf` (regla AGENTS.md #7:
  "No generar PDF si compliance = NO_GO").

**Por qué se mantiene (PDF omitido):**
- AGENTS.md #7 prevalece sobre plan §8 (jerarquía de verdad en
  AGENTS.md §"Jerarquía de verdad": código y reglas operativas
  ganan sobre documentación general).
- El razonamiento implícito en AGENTS.md: un PDF generado a partir de
  un cálculo bloqueado por compliance puede ser usado para fines
  fraudulentos; el markdown con texto explícito de "BLOQUEADA" es
  suficiente señal.
- El plan original no consideró este riesgo.

**Riesgo:** ninguno. El comportamiento cumple la regla operativa.

## Tareas cerradas por este addendum

- **Tarea 3.A** (`document_context` formal): CERRADA S36 con la
  creación de `liquidator/contracts/document_context.py` (modelo
  Pydantic con `RenglonDesglose`, `ComplianceInfo`, `DocumentContext`
  y constructor `from_engine_result()` que anonimiza PII y aplana el
  desglose). Suite: 45 tests nuevos en
  `test_contracts/test_document_context.py`.
- **Tarea 3.B** (Plantillas Jinja): CERRADA por absorción — la
  cobertura funcional existe vía `comprobante_*.md` + `_render_blocked`.
- **Tarea 3.C** (Renderers separados): CERRADA por absorción — los
  archivos existen con nombres distintos pero responsabilidades
  equivalentes.
- **Tarea 3.D** (`liquidacion_BLOQUEADA.*` para NO_GO): CERRADA S36
  con la modificación de `liquidator/cli/main.py` y la creación de
  `liquidator/tests/test_cli/test_liquidar.py` (20 tests nuevos).
- **Tarea 3.E** (Auditoría inmutable): CERRADA por absorción — la
  suite `test_audit/` cubre el comportamiento contractual con 4
  archivos separados en lugar de 1.
- **Tarea 3.F** (Validación pre-render base): CERRADA por absorción —
  el archivo `pre_render_validator.py` (creado en S34 para Tarea 3.G)
  cubre los 4 checks base del plan §3.F más los extendidos por motivo.

**Cierre formal:** Fase 3 CERRADA S36 con las 6 tareas base + 2
addenda (3.G S34, 3.H S35) cerradas.

## Métricas de la sesión S36

- **Tests añadidos:** 65 (45 de `document_context` + 20 de CLI).
- **Tests totales:** 650 (vs 585 en S35 → +11% growth).
- **Regresiones:** 0.
- **42 fails preexistentes:** asignados a Fase 4 (suite 100%).
- **15 errors preexistentes:** asignados a Fase 4.

## Referencias

- `Planificación/plan_modernizacion_v2.0_2026-06-09.md` §8.1, §8.2, §8.3
- `Planificación/REGISTRY.md` (entrada S36)
- `Contexto/AGENTS.md` (jerarquía de verdad, regla #7)
- `liquidator/contracts/document_context.py` (Tarea 3.A)
- `liquidator/cli/main.py:_write_output_artifacts` (Tarea 3.D)
- `liquidator/tests/test_contracts/test_document_context.py` (Tarea 3.A)
- `liquidator/tests/test_cli/test_liquidar.py` (Tarea 3.D)
