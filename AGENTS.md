# Reglas para agentes que operan en liquidacion_cli

> Leer este archivo al ABRIR cualquier sesión. Son reglas inamovibles:
> violar una sola puede producir bugs legales con consecuencias reales.
> Si encontrás una contradicción entre este archivo y el código vivo,
> **gana el código** (y reportá la discrepancia en `REGISTRY.md`).

## Jerarquía de verdad (en orden descendente de autoridad)

1. **Código vivo en `liquidator/`, `params/`, `legal_docs/`, `tests/`.**
   Única fuente ejecutable. Si una nota de KB dice X y el `import`
   resuelve Y, Y gana.
2. **Parámetros versionados.** `params/<año>.json` (2025, 2026 vigentes),
   `params/normas.json`, `params/plazos.json`, `params/checklist.json`.
   Son contrato motor-agente: modificarlos sin versionar es incidente
   de auditoría.
3. **Tests reales y resultados de ejecución.** Lo que la suite verifica
   hoy es lo que el motor hace hoy. Un test que falla es un bug o una
   regresión, no una "inconsistencia menor".
4. **Diagnóstico `docs/audit/diagnosticos/diagnostico_inicial_2026-06-09.md`.**
   Mapa de riesgos conocido, pero contrastado contra código: fue
   escrito en una pasada y puede tener errores (§5.10 del diagnóstico
   y `Contexto/KB_LLM/06_riesgos_modelo.md`).
5. **KB local `Contexto/KB_LLM/`.** Resumen operativo, no verdad. Si
   una nota tiene más de 30 días sin revalidar contra código, tratarla
   como sospechosa. Cada nota debe tener footer "Última validación
   contra código" con fecha.
6. **Documentación general `docs/`, `README.md`, `QWEN.md`.** Última en
   la jerarquía. Contexto histórico; no refleja estado del motor. Se
   reescribirá en Fase 4 (release v2.0).

**Regla de oro:** si una afirmación de la KB, del diagnóstico o de `docs/`
contradice lo que ejecuta el código, **gana el código**. Documentar la
contradicción en `Contexto/KB_LLM/06_riesgos_modelo.md` con archivo y
línea.

## Reglas operativas inamovibles

1. **Leer params antes de calcular.** Antes de cualquier operación de
   cálculo, leer `params/<año>.json` (todos los vigentes),
   `params/normas.json`, `params/plazos.json`.
2. **Verificar reglas legales contra evidencia.** Antes de confiar en
   una cita legal, buscar evidencia en `params/normas.json` (entrada
   con `id`, `url`, `vigencia`) o en `legal_docs/`. Si no está en
   ninguno, marcar `PENDIENTE_VERIFICAR` y NO usarla para cálculo.
3. **Contrastar documentación contra código.** Antes de aceptar
   cualquier afirmación del diagnóstico o de la KB como verdad,
   verificar contra código vivo, params y tests.
4. **No hardcodear valores.** Nunca hardcodear SMMLV, auxilio de
   transporte, límites salariales, tasas, plazos ni ningún valor
   paramétrico. Todo debe leerse de `params/<año>.json`.
5. **No usar outputs como fuente de verdad.** `output/` y
   `output/_legacy/` son artefactos, no contrato. Nunca copiarlos
   como "expected values" sin firma explícita de quién los validó.
6. **Anonimizar datos sensibles.** No incluir nombres reales,
   documentos de identidad, salarios reales ni datos sensibles en
   la KB, logs, ejemplos o commits. Usar `[ANONIMIZADO]`.
7. **No generar PDF si compliance = `NO_GO`.** Override documentado
   solo con `operator_id` (≥3 chars) y `override_reason` (≥10 chars).
8. **No disfrazar `.txt` como PDF.** La extensión del archivo debe
   corresponder a su formato real. Si el motor no puede generar PDF
   legítimo, entregar `.md` o `.txt` con advertencia explícita.
9. **Separar claramente los estados de compliance.** GO, WARN, NO_GO,
   OVERRIDE_APPROVED deben ser explícitos en todo output y log. Cada
   regla en `params/checklist.json` tiene su severidad (CRITICAL,
   HIGH, MEDIUM, LOW, INFO).
10. **Trazabilidad completa.** Cada documento generado debe incluir
    qué `params_version`, `normas_version` y reglas de compliance usó.
    El output debe ser auditable sin acceso al código fuente.
11. **Código > documento.** Antes de aceptar como verdad cualquier
    afirmación del diagnóstico 2026-06-09 o de la KB, verificar contra
    código vivo. Si discrepan, código gana; documentar en
    `06_riesgos_modelo.md`.
12. **Caso canónico como smoke test.** Antes de cerrar cualquier fase,
    ejecutar el caso canónico (206 días, SBL 2.200.000, segmentos
    46d+160d). Si falla, la fase no se cierra: es bug del motor en
    fase anterior.

## Caso canónico

Ver `Contexto/KB_LLM/09_caso_canonico_usuario.md` para el input completo.

- **Modo:** PERIODICA, 206 días en 2 segmentos (2025-H2: 46d + 2026-H1: 160d)
- **SBL:** 2.200.000 (constante ambos años)
- **Params:** `params/2025.json` + `params/2026.json`
- **Convención de días:** inclusiva en ambos extremos

**Regla:** este caso DEBE ejecutarse y pasar antes de cerrar cualquier
fase. Si falla, la fase objetivo no se cierra. La primera ejecución
end-to-end ocurre en Fase 1 Tarea 1.B (golden test).

## Cómo correr la suite

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
PYTHONPATH=. uv run --with pytest --with python-dateutil --with PyYAML \
  --with jsonschema --with pydantic --with loguru --with click \
  --with markdown --with Jinja2 pytest liquidator/tests -q
```

`PYTHONPATH=.` es obligatorio. Sin él, los imports relativos del
motor fallan.

## Trampas conocidas (no violar)

1. **No cerrar sesión sin los 5 pasos del cierre** (validar DoD,
   actualizar REGISTRY, CHANGELOG, sincronizar KB, verificar addendas).
2. **No hardcodear SMMLV, aux_trans, tasas, plazos.** Siempre leer
   `params/<año>.json`. Grep `liquidator/` si hay duda.
3. **No generar PDF si compliance = `NO_GO`.** Override solo con
   `operator_id` documentado.
4. **No disfrazar `.txt` como PDF.** Extensión = formato real.
5. **No usar outputs como expected values** sin firma del usuario.
   `output/_legacy/` es histórico, no contrato.
6. **Prescripción de prestaciones = Art. 488 CST, NO Art. 155**
   (riesgos R-LEG-02, R-LEG-03). Cualquier referencia operacional a
   Art. 155 en `liquidator/`, `params/` o `legal_docs/` es bug.
7. **No inventar URLs de SUIN/Juriscol.** Si una norma no tiene `url`
   verificada en `params/normas.json`, está `PENDIENTE_VERIFICAR`;
   reportar como tal.
8. **No citar leyes o decretos sin `id` en `params/normas.json`.**
   Las citas "al vuelo" son el origen #1 de bugs legales.
9. **No aceptar la salida de otro agente sin re-verificar.** Si un
   subagente dice "el test pasa", correr el test vos mismo.
10. **SL2630-2024 y Art. 189 párr. 1° CST** están `PENDIENTE_VERIFICAR`
    (reparos bloqueantes de addendas). No usarlos para cálculo sin
    verificación verbatim de URL/sala/texto en SUIN.
11. **Indemnización Art. 64 CST NO implementada en v2.0** (R-LEG-01).
    Output debe traer `indemnizacion: null`. Si el caso real la
    requiere, derivar a Fase 4+ (post-release).
12. **No hacer `git init` antes de Tarea 0.A** (clave de cifrado
    rotada en S1). No hacer primer `git add` antes de Tarea 0.B
    (`.gitignore` debe existir primero).
13. **Eliminaciones pospuestas** (decisión S3): `__pycache__/`,
    `htmlcov/`, `.coverage`, `*.egg-info/`,
    `documentos_legales_rurales/`. NO borrar sin que el usuario lo
    pida de nuevo.
14. **Un agente que dice "no sé, falta verificar" es más valioso
    que uno que inventa una respuesta coherente.**
15. **SMMLV 2026 ($1.750.905) está vigente por Decreto 159/2026**
    (transitorio, re-fijación del 2026-02-19), NO directamente por
    el Decreto 1469/2025 (suspendido provisionalmente por Auto del
    Consejo de Estado del 2026-02-12, Exp. 11001-03-25-000-2026-00004-00).
    El valor es el mismo en ambos actos, así que **el motor no
    necesita cambios**; pero el output de cualquier liquidación con
    `fecha_corte >= 2026-01-01` debe listar **ambos decretos** en
    `meta.referencias_normativas` (ver `Contexto/KB_LLM/05_schema_salida.md`).
    Vigilar nulidad del Decreto 1469/2025 antes de v2.0 release (R-LEG-07);
    si la nulidad prospera, el SMMLV 2026 vuelve a 1.423.500 con
    retroactivo.
16. **No aplicar la entrada `LEY_2466_2025_INTERESES_MENSUALES`** de
    `params/normas.json` para cálculo de pago mensual de intereses
    sobre cesantías hasta que se verifique el artículo literal exacto
    de la Ley 2466/2025. Verificación SUIN del 2026-06-13 muestra
    que el Art. 64 de la Ley 2466/2025 es "Régimen simple laboral",
    NO pago mensual de intereses (R-LEG-06, bloqueante). Mientras
    tanto, usar la regla vigente (Ley 50/1990 Art. 99): pago
    **anual** único el 31 de enero, tasa 12% sobre cesantías al
    31 de diciembre del año anterior.

## Cierre de sesión (5 pasos, en este orden)

1. **Validar DoD contra código vivo.** Re-correr la validación que el
   plan especifica para la tarea: `compileall`, `wc -l`, `pytest`, etc.
   Si el código falla, la tarea no está cerrada.
2. **Actualizar `Planificación/REGISTRY.md`.** Cambiar estado de
   fase/tarea, agregar fila al log de cierres (una por sesión, más
   reciente arriba), actualizar "Estado actual".
3. **Si se cerró una fase**, agregar entrada en `CHANGELOG.md` bajo
   `[Unreleased]`. Incluso para sub-tareas dentro de una fase,
   `[Unreleased]` debe crecer.
4. **Si se modificaron params o reglas**, sincronizar la nota KB
   correspondiente (`Contexto/KB_LLM/02` para params, `03` para
   compliance). Actualizar footer "Última validación contra código".
5. **Si se tocó un addenda**, verificar que la decisión aprobada no
   haya cambiado. Si cambió, documentar en el addenda y re-evaluar
   aprobaciones.

**No cerrar sesión sin completar los 5 puntos.**

## Referencias rápidas

| Archivo | Qué contiene | Cuándo leerlo |
|---------|-------------|---------------|
| `Planificación/REGISTRY.md` | Estado de fases, log de sesiones, próxima tarea | ABRIR SESIÓN (primero) |
| `Planificación/plan_modernizacion_v2.0_2026-06-09.md` | Plan completo (3.353 líneas) | Solo para detalle de tarea |
| `Contexto/KB_LLM/00_fuente_de_verdad.md` | Jerarquía de verdad, regla de oro | Duda sobre qué fuente prevalece |
| `Contexto/KB_LLM/01_reglas_calculo.md` | Fórmulas y citas legales por concepto | Tareas de cálculo |
| `Contexto/KB_LLM/02_parametros_vigentes.md` | SMMLV, aux_trans por año | Toda tarea de cálculo |
| `Contexto/KB_LLM/03_compliance_blocking.md` | GO/WARN/NO_GO/OVERRIDE, reglas V001-V010 | Tareas de compliance |
| `Contexto/KB_LLM/06_riesgos_modelo.md` | 12 riesgos tipificados (R-LEG, R-OP, R-SEC) | Evaluar impacto de cambios |
| `Contexto/KB_LLM/09_caso_canonico_usuario.md` | Input y valores esperados del caso ancla | Antes de cerrar cualquier fase |
| `Contexto/prompts/` | 3 prompts operativos (generación, auditoría, planificación) | Sesiones LLM-driven |
| `CHANGELOG.md` | Historial de cambios por versión | Auditar decisiones pasadas |
| `params/<año>.json` | SMMLV, aux_trans, UVT del año | NUNCA hardcodear; siempre leer |
| `params/normas.json` | Citas legales con URL y vigencia | Antes de usar cualquier cita |
| `params/checklist.json` | Reglas de compliance con severidad | Validar output |

---
**Última actualización:** 2026-06-13 — sesión S7, Tarea 0.G (creación de AGENTS.md).
**Fuente:** plan v2.0 §5.2 T0.G (líneas 362-404), KB_LLM/00, KB_LLM/09,
REGISTRY.md, prompts de Contexto/prompts/.
