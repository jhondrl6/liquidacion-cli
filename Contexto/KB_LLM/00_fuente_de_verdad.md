# 00 — Fuente de verdad (jerarquía y regla de oro)

> Nota ancla de la KB. Toda otra nota de `Contexto/KB_LLM/` que contradiga
> esta sección está equivocada. Si encontrás una contradicción entre esta KB
> y el código vivo, **gana el código vivo**.

## Jerarquía de verdad (en orden descendente de autoridad)

1. **Código vivo en `liquidator/`, `params/`, `legal_docs/`, `tests/`.**
   Es la única fuente ejecutable. Si una nota de esta KB dice una cosa y el
   `import` resuelve otra, el `import` gana.
2. **Parámetros versionados.** `params/<año>.json` (2025 y 2026 vigentes),
   `params/normas.json`, `params/plazos.json`, `params/checklist.json`.
   Son contrato entre motor y agente: cambiarlos sin versionar es un
   incidente de auditoría.
3. **Tests reales y resultados de ejecución.** Lo que la suite verifica hoy
   es lo que el motor hace hoy. Un test que falla es un bug o una regresión,
   no una "inconsistencia menor".
4. **Diagnóstico `Contexto/diagnostico_liquidacion_cli_2026-06-09.md`.**
   Útil como mapa de riesgos conocido, pero contrastado contra código: fue
   escrito en una sola pasada y puede tener errores (ver §5.10 del
   diagnóstico y `06_riesgos_modelo.md`).
5. **KB local `Contexto/KB_LLM/`.** Esta carpeta. Es resumen operativo,
   no verdad. Si una nota tiene más de 30 días sin revalidar contra código,
   trátala como sospechosa.
6. **Documentación general `docs/`, `README.md`, `QWEN.md`.** Última en la
   jerarquía. Contiene contexto histórico pero no refleja estado del motor.
   Se reescribirá en Fase 4 (release v2.0).

## Regla de oro

> **Si una afirmación de la KB, del diagnóstico o de un docs contradice lo
> que ejecuta el código, gana el código.** Documentar la contradicción en
> `06_riesgos_modelo.md` con referencia a commit, archivo y línea.

## Cómo se aplica esta jerarquía en la práctica

- Antes de **calcular** una liquidación: leer `params/<año>.json`
  correspondiente al año del segmento. Nunca copiar valores del año anterior
  sin verificar el decreto vigente.
- Antes de **confiar** en una cita legal: buscar evidencia en
  `params/normas.json` (entrada con `id`, `url`, `vigencia`) o en
  `legal_docs/`. Si la cita no está en ninguno de los dos, marcarla como
  `PENDIENTE_VERIFICAR` y NO usarla para cálculo.
- Antes de **modificar** un parámetro: leer `CHANGELOG.md` y `REGISTRY.md`
  para saber si hubo una decisión previa documentada. Si la hubo, respetarla
  o re-evaluar la decisión (nunca sobrescribir silenciosamente).
- Antes de **cerrar sesión**: ejecutar los 5 pasos de "Regla de cierre de
  sesión" en `REGISTRY.md` (validar DoD, actualizar REGISTRY, CHANGELOG,
  KB, addenda).

## Lo que NO es fuente de verdad

- Outputs generados en `output/`, `output/_legacy/`, `audit/`: artefactos,
  no contrato. Nunca copiarlos como "expected values" sin firma de quién
  los validó.
- Memoria de sesión previa o de la IA: volátil. Lo que se decida entre
  sesiones debe escribirse en `REGISTRY.md`, `CHANGELOG.md` o en la KB.
- Forks o copias de trabajo en `__pycache__/`, `.venv/`, `htmlcov/`,
  `*.egg-info/`, `documentos_legales_rurales/`: ignorados por `.gitignore`
  por hygiene; no contienen información de negocio.
- `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`: caché de
  herramientas; no son fuente.

## Estado de la KB (sesión de creación)

- **Sesión de creación:** S5 — 2026-06-12/13 (Tarea 0.E del plan v2.0).
- **Estado de Fase 0 al crearse esta nota:** 0.A ✓, 0.B ✓, 0.C ✓, 0.D ✓
  (ver `REGISTRY.md` log de cierres). Pendientes: 0.E (esta tarea), 0.F,
  0.G, 0.H, 0.I, 0.J, 0.K.
- **Sesión de sincronización (S6):** S6 — 2026-06-13 (Tarea 0.F). Capa
  operativa de la KB en `Contexto/prompts/` (3 prompts: generación,
  auditoría, planificación). **Para invocar estas reglas en una sesión
  LLM, usar el prompt apropiado de `Contexto/prompts/`** — los prompts
  codifican la misma jerarquía y reglas, con formato de respuesta
  obligatorio y trampas operativas.
- **Sesión de sincronización (S7):** S7 — 2026-06-13 (Tarea 0.G).
  `AGENTS.md` creado en raíz (183 líneas): es la capa de reglas
  inamovibles para agentes — contiene la misma jerarquía de verdad,
  las 12 reglas operativas, las trampas conocidas consolidadas de
  REGISTRY + prompts, y una tabla de referencias rápidas. **AGENTS.md
  es lectura obligatoria al abrir sesión** (junto con REGISTRY.md
  "Estado actual").
- **Convención de versionado de notas:** cada nota lleva al final una
  sección "Última validación contra código" con fecha. Antes de usarla
  en una sesión >30 días, re-validar.
