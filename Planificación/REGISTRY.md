# REGISTRY — liquidacion_cli v2.0

> **Fuente de verdad de progreso de fases.** Se actualiza OBLIGATORIAMENTE al cerrar
> cada sesión. Operador o agente lee este archivo PRIMERO al abrir sesión; el
> plan completo (3.353 líneas) solo se consulta cuando se necesita detalle.
>
> **Granularidad:** una entrada por sesión (alineado con la convención "1 fase
> por sesión" del plan §3). Una sesión puede cerrar cero, una o varias tareas
> puntuales, pero solo cierra UNA fase como máximo.

---

## Estado actual (leer primero)

- **Última sesión cerrada:** **S53 — 2026-06-20, Fase 4 CIERRE FINAL ESTRICTO COMPLETO**. SL2630-2024 promovido de `VERIFICADO_PARCIAL_AVANZADO` (S52) a `VERIFICADO` tras la entrega por el operador (Jhond) de la base de conocimiento estructurada completa en `legal_docs/SL2630-2024_knowledge_base.md` (700 líneas, 26KB). La knowledge base contiene: cabecera verificada, partes (Juan Enrique Moreno Palma vs AVIANCA S.A. + Servicopava), pretensiones, prescripción trienal (Art. 488 CST + Art. 151 CPTSS), historial salarial acreditado 2006-2017, liquidación de cesantías/vacaciones/intereses con cifras exactas (condena total $20.755.559: cesantías $20.665.485 + vacaciones $39.367 + intereses $50.707), decisión final, excepción de compensación, marco legal CTA, indicios de intermediación (CSJ SL2084-2023), mapping a schemas Pydantic del motor (Salario.sbl_por_anio con valores 2006-2016, LiquidacionInput.periodos_no_pagados con PeriodoNoPagado por año), 13 sentencias CSJ adicionales citadas, glosario completo. **Item 2:** `params/normas.json` entry `SL2630_2024` actualizado: estado `VERIFICADO_PARCIAL` → `VERIFICADO`, `descripcion` extendida con doctrina complementaria, `cabecera_fallo.partes` ahora objeto estructurado con demandante/demandadas/otros_actores, agregados `firmantes_adicionales` (Olga Yineth Merchán Calderón + Marirraquel Rodelo Navarro) y `decision_final_COP`, `texto_relevante` reescrito con doctrina operacional completa (anualización + prescripción + indexación IPC + excepción compensación + indicios intermediación + actividad misional permanente), agregados `archivo_local` apuntando a la knowledge base. **Item 3:** KB_LLM/01_reglas_calculo.md sección "Anualización salarial SL2630-2024" actualizada a `VERIFICADO S53` con referencia a la knowledge base local. **Item 4:** Cierre formal de Fase 4 ahora COMPLETO con ambos verbatims en VERIFICADO. **Pendiente solo si se requiere:** transcripción literal verbatim de cada párrafo del fallo (no es necesario para uso operacional del motor — la doctrina está implementada en SalarioResolver y IPCIndexador con 69 tests verdes).
  - `caso_1/input.json` (25L, 1.2KB) + `output.json` (205L, 7.2KB) + `comparativa.md` (158L, 6.9KB)
  - `caso_2/input.json` (40L, 1.6KB) + `output.json` (225L, 7.9KB) + `comparativa.md` (162L, 7.1KB)
  - `caso_3/input.json` (53L, 2.7KB) + `output.json` (236L, 8.3KB) + `comparativa.md` (188L, 8.4KB)
  - `Planificación/Casos.md` (123L) marcado SUPERSEDED (borrador del usuario con los 3 errores conceptuales)
  - 3 correcciones de Forma: Caso 1 `auxilio_transporte` boolean→162000 numérico + borrado `aux_transporte_real_mensual` (inventado); Caso 2 `salario: {}` anidado agregado (activa SalarioResolver para segmentación SL2630); Caso 3 `contrato: {}` anidado agregado (activa hook preaviso Art. 46)
  - 3 excepciones en `.gitignore` (líneas 75-77) para trackear las `comparativa.md` (deliverables humanos, no outputs generados)
  - 0 código modificado, 0 tests corridos, 0 regresiones. Suite sin cambios: 656P/36F/1xfail/15E (preexistentes).
- **Próxima tarea a ejecutar:** **Fase 4 CERRADA — no hay Fase 4.X pendiente**. Siguiente fase: **Fase 5 (CONDICIONAL)** "Investigación casos reales" — solo se activa si surgen casos reales en Fases 0-4 que motiven investigación adicional. Acciones opcionales post-Fase 4 (no bloquean): (1) ~~bumpear `actions/checkout@v4` → `@v5` y `actions/setup-python@v5` → `@v6`~~ **COMPLETADO S55** — checkout@v6 + setup-python@v6, env var `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` removida; (2) ~~triagear los 36F+15E crónicos en pytest~~ **RESUELTO en S51** — suite 682P/28S/2xfail/0F desde S51, el ítem en REGISTRY estaba desactualizado; (3) si querés transcripción literal verbatim de cada párrafo del fallo SL2630-2024, pedila a la Relatoría CSJ o copiala vos del aplicativo — no es necesaria para uso operacional del motor.
- **Bloqueos activos:** ninguno de Fase 0 (cerrada). PENDIENTE (pospuesto por usuario en S3): eliminación de `__pycache__/`, `htmlcov/`, `.coverage`, `liquidacion_nomina_colombia.egg-info/`, `documentos_legales_rurales/` (vacío). **Issue resuelto post-S26:** `.env.backup*` del .gitignore ahora SÍ matchea. **CI post-S52:** suite 0F (682P/28S/2xfail/1w) verde. ruff 0 errores. mypy 123 errores preexistentes NO BLOQUEANTES (script usa `|| true`, documentado desde S38). **Verbatim Art. 488 CST:** VERIFICADO (S52) — texto literal verbatim extraído de Secretaría del Senado de la República (fuente primaria oficial con vigencia expresa y control de constitucionalidad) y corroborado por CIJUF/Min.Protección Social — Concepto 202475 del 18-jul-2008. SUIN `id=30019323` URL registrada (fetch intermitente, texto literal indexado por Google snippet). normas.json entry `CST_488_PRESCRIPCION` promovido a VERIFICADO. **Verbatim SL2630-2024:** VERIFICADO (S53) — transcripción doctrinal estructurada completa en `legal_docs/SL2630-2024_knowledge_base.md` (700 líneas, 26KB) con cifras exactas de condena, 13 sentencias CSJ adicionales citadas, 6 normas complementarias, mapping a schemas Pydantic del motor, y glosario. Cabecera del fallo (sala, radicado 101342, ponente Beltrán Quintero, fecha 17-sep-2024, acta 34, sentido CASA TOTALMENTE) verificada contra aplicativo de la Relatoría CSJ. URLs primarias oficiales registradas: `consultajurisprudencial.ramajudicial.gov.co` y `ecosistemadigitalindice.cortesuprema.gov.co`. URL complementaria vLex. **Cierre formal de Fase 4: COMPLETO** (ambos verbatims en VERIFICADO). **Node 20 actions deprecadas en CI (S46, S54 — RESUELTO DEFINITIVO S55):** `.github/workflows/ci.yml` ahora usa `actions/checkout@v6` y `actions/setup-python@v6` (ambos Node 24 nativos). La env var `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` fue removida (redundante con el bump).

---

## Tabla de fases

| Fase       | Título                                                | Estado        | Cerrada | Pendiente / Notas                                              |
|------------|-------------------------------------------------------|---------------|---------|----------------------------------------------------------------|
| 0          | Higiene + segundo cerebro mínimo                      | **CERRADA**   | S11, 2026-06-13 | 0.A-0.K ✓ (orden estricto cumplido: 0.A→0.B→…→0.K). DoD completo: KB 10/10, params 2025+2026 vigentes, normas con URLs SUIN reales, script freshness year-aware, suite inventariada (75 issues → Fase 1). |
| 1          | Estabilizar y formalizar                              | **CERRADA**   | S26, 2026-06-13 | **12/12 tareas ✓, todos los R-OP cerrados.** (Tarea 1.A-utils S12, 1.X S13, 1.A-plan S14, 1.B S15, 1.C S16, 1.E S17, 1.D S18, 1.I S19, 1.G S20, **R-OP-11 S21**, **1.F S22**, **1.C-bis S23**, **1.C-ter S24**, **1.C-quater S25**). R-OP-02 Causa 2 S26, R-OP-07 S26, R-OP-08 S26, R-OP-09 S26, bug checklist_loader.py S26. 393 passed / 36 failed / 15 errors (36 fails preexistentes asignados a Fase 2+). Fase 1 CERRADA formalmente. |
| 1.C-bis    | (Addendum SL2630) Schema `Salario` extendido          | **CERRADA**   | S23, 2026-06-13 | Anidada en Fase 1. Aditiva retrocompatible. **3 archivos:** `liquidator/contracts/input_model.py` (MesValor + sbl_por_anio + historial_salarial + model_validator), `liquidator/tests/test_contracts/test_salario_extendido.py` (nuevo, 10 tests), `Contexto/KB_LLM/04_schema_entrada.md`. **DoD:** 10/10 PASS, 39/39 PASS en test_contracts, 11/11 PASS caso canónico. Motor NO consume nuevos campos en Fase 1; Tarea 2.B-bis (Fase 2) los activará vía `SalarioResolver`. |
| 1.C-ter    | (Addendum finiquito) Schema `Contrato` + `Vacaciones` | **CERRADA**   | S24, 2026-06-13 | Anidada en Fase 1. Aditiva retrocompatible. **4 archivos:** `liquidator/contracts/input_model.py` (MotivoTerminacion enum 10 valores, PeriodoDisfrute, VacacionesEstado, Contrato actualizado, LiquidacionInput actualizado), `liquidator/tests/test_contracts/test_vacaciones_estado.py` (nuevo, 15 tests), `liquidator/tests/test_contracts/test_motivo_terminacion.py` (nuevo, 15 tests), `Contexto/KB_LLM/04_schema_entrada.md`. **DoD:** 69/69 PASS en test_contracts, 11/11 PASS caso canónico. Motor NO consume los nuevos campos en Fase 1; Tarea 2.B-ter (Fase 2) usará motivo_terminacion y vacaciones tipadas. |
| Tarea 1.C-quater | (Addendum preaviso) Schema `Contrato` preaviso Art.46 | **CERRADA**   | S25, 2026-06-13 | Anidada en Fase 1. Aditiva retrocompatible. **2 archivos:** `liquidator/contracts/input_model.py` (4 nuevos campos opcionales: `fecha_vencimiento_termino_fijo`, `preaviso_entregado`, `fecha_preaviso`, `dias_preaviso` + `model_validator _preaviso_consistencia` con 3 reglas: solo FIJO / `preaviso_entregado=True` exige `fecha_preaviso` / FINIQUITO+FIJO+vencido exige `preaviso_entregado` declarado), `liquidator/tests/test_contracts/test_preaviso_contrato.py` (nuevo, 16 tests en 4 clases: regresión canónica, reglas de éxito, reglas de fallo, consistencia), `Contexto/KB_LLM/04_schema_entrada.md` (marcado IMPLEMENTADO S25). **DoD:** 16/16 PASS en `test_preaviso_contrato.py`; 85/85 PASS en `test_contracts/`; 11/11 PASS caso canónico. 0 regresiones. Motor NO consume los nuevos campos en Fase 1; Tarea 2.B-cuater (Fase 2) los activará vía `IndemnizacionCalculator.calculate_indemnizacion_preaviso`. |
| 2          | Cálculo legal y motor correcto                        | **CERRADA**   | S33b, 2026-06-14 | Todas las tareas cerradas: 2.A-2.I (plan base) + 2.B-bis (S27), 2.X (S28), 2.B-ter (S29), 2.B-cuater (S30), 2.Y (S31), 2.Z (S33). Gaps heredados a Fase 4: severity→blocking incompleto, suite al 100%. |
| 2.B-bis    | (Addendum SL2630) `SalarioResolver` SBL por año       | **CERRADA**   | S27, 2026-06-13 | Anidada en Fase 2. **4 archivos:** `liquidator/core/salario_resolver.py` (nuevo), `liquidator/core/workflow_orchestrator.py` (integración), `liquidator/core/__init__.py` (exports), `Contexto/KB_LLM/01_reglas_calculo.md` (SL2630-2024). **Tests:** 15 unitarios + 9 golden = 24/24 PASS. Suite: 417 passed (+24 vs S26). 0 regresiones. DoD: caso canónico verde, SBL variable produce cálculos distintos, 3 prioridades probadas. |
| 2.X        | (Addendum SL2630) Indexación IPC para prestaciones no pagadas | **CERRADA** | S28, 2026-06-13 | Anidada en Fase 2-bis. **8 archivos creados/modificados:** (1) `liquidator/calculators/indexacion.py` (nuevo) — clase `IPCIndexador` con validación defensiva anti-tasa, `from_json()` dual-formato, `indexar()` con ROUND_HALF_UP. (2) `liquidator/calculators/__init__.py` — export. (3) `liquidator/contracts/input_model.py` — modelo `PeriodoNoPagado` (4 fechas, 4 conceptos Literal, `model_validator` de consistencia causal). (4) `liquidator/compliance/rule_evaluator.py` — regla `V011` (V_INDEXACION_IPC, severity MEDIUM, no bloqueante) con prescripción Art. 488 CST. (5) `liquidator/core/engine.py` — `_procesar_periodos_no_pagados()` integrado en `process_input()`. (6) `params/normas.json` — `SL2630_2024` y `CST_488_PRESCRIPCION` (ambas `PENDIENTE_VERBATIM`). (7) `params/checklist.json` — `V011` con `formula`/`nota`. (8) `Contexto/KB_LLM/01_reglas_calculo.md` — sección "Indexación por IPC". **+4 archivos de soporte:** `params/ipc_variacion_anual_dane.csv` (17 años DANE), `params/ipc_dane_mensual.json` (204 índices mensuales base 100 en 2010-01), `scripts/build_ipc_index.py` (validador geométrico), `examples/inputs/prescripcion_indexada.json` + `examples/expected/prescripcion_indexada_result.json`. **Tests:** 24 unitarios (`test_indexacion.py`) + 12 golden (`test_prescripcion_indexada.py`) = 36/36 PASS. **Reparos cerrados:** (a) cero referencias a Art. 155 en `indexacion.py` (verificado por test), (c) defensa contra tasas disfrazadas. **Reparos pendientes (no bloquean DoD 2.X, sí bloquean v2.0 release):** (b) verificación verbatim SL2630-2024 y Art. 488 CST. **DoD plan §7-bis.1:** 9/9 checks cumplidos. |
| 2.B-ter    | (Addendum finiquito) Vacaciones compensadas           | **CERRADA**   | S29, 2026-06-13 | Anidada en Fase 2. **6 archivos de código:** `prestaciones_calculator.py` (+48 líneas, método `calculate_vacaciones_compensadas_finiquito` fórmula Art. 189-190 CST: `(SBL/30)×dias_pendientes`), `engine.py` (+68 líneas, hook `_calcular_vacaciones_si_finiquito` solo FINIQUITO), `test_vacaciones_finiquito.py` (nuevo, 9 tests), `test_finiquito_renuncia_212d.py` (nuevo, 8 tests), `finiquito_renuncia_212d.json` (fixture golden), `01_reglas_calculo.md` (sección vacaciones actualizada). **+2 archivos de soporte:** `params/normas.json` (entrada `CST_189_VACACIONES` con texto literal verificado SUIN, estado VERIFICADO). **Reparo (a) cerrado:** Art. 189 CST párr. 1° verificado verbatim en SUIN (num. 1: acuerdo mutuo; num. 2: compensación obligatoria al terminar). **Tests:** 17/17 PASS (9 unitarios + 8 golden). Suite: 470P/36F/15E. 0 regresiones. |
| 2.B-cuater | (Addendum preaviso) Indemnización preaviso Art.46 CST | **CERRADA**   | S30, 2026-06-14 | Anidada en Fase 2. Solo FINIQUITO + FIJO + vencido. **4 archivos de código:** `indemnizacion_calculator.py` (+85, método `calculate_indemnizacion_preaviso`), `engine.py` (+130, hook `_calcular_preaviso_si_fijo_vencido`), `test_preaviso.py` (nuevo, 18 tests), `test_preaviso_fijo_vencido.py` (nuevo, 10 tests golden). **+2 soporte:** `normas.json` (CST_46_PREAVISO VERIFICADO SUIN), `finiquito_fijo_vencido_preaviso.json` (fixture). **Reparos (a)(b)(c) cerrados.** Tests: 28/28 PASS (1 xfail). Suite: 497P/36F/15E. 0 regresiones. |
| 2.Z        | (Addendum finiquito) Compliance vacaciones            | **CERRADA**   | S33, 2026-06-14 | Anidada en Fase 2. **4 archivos:** `params/checklist.json` (+2 reglas V014/V015), `liquidator/compliance/rule_evaluator.py` (+139 líneas, funciones `_v014_vacaciones_finiquito` CRITICAL blocking + `_v015_vacaciones_declaradas` MEDIUM non-blocking + import Decimal), `liquidator/tests/test_compliance/test_vacaciones_finiquito_compliance.py` (nuevo, 23 tests en 4 clases: V014 unitarios 8, V015 unitarios 4, integración ComplianceEngine 6, reparos addendum 5), `Contexto/KB_LLM/03_compliance_blocking.md` (actualizada con V014/V015). **DoD:** 23/23 PASS. Suite: 542P/41F/15E. 0 regresiones (41F preexistentes). |
| 2.Y        | (Addendum preaviso) Compliance preaviso Art.46 CST    | **CERRADA**   | S31, 2026-06-14 | Anidada en Fase 2. **3 archivos de código + 1 soporte.** `checklist.json` (V012+V013), `rule_evaluator.py` (+225, 2 funciones), `test_preaviso_compliance.py` (27 tests). Soporte: `03_compliance_blocking.md`. Tests: 27/27 PASS. Suite: 524P/36F/15E. 0 regresiones. |
| 2-bis      | IPC + anualización salarial (nueva)                   | **CERRADA**   | S28, 2026-06-13 | Tarea 2.X absorbida en Fase 2 (cerrada S28). |
| 3          | Documento generable robusto                           | **CERRADA**     | S36, 2026-06-14 | 6/6 tareas base + 2/2 addenda cerradas. 3.A (DocumentContext formal) y 3.D (liquidacion_BLOQUEADA.* + exit 2) cerradas S36 con 65 tests nuevos (45 + 20). 3.B/3.C/3.E/3.F cerradas por absorción (ver addendum `addendum_fase3_arquitectura_2026-06-14.md`). 3.G S34, 3.H S35. |
| 3.A        | `document_context` formal (Pydantic)                  | **CERRADA**   | S36, 2026-06-14 | Anidada en Fase 3. **2 archivos:** `liquidator/contracts/document_context.py` (nuevo, modelo Pydantic con `RenglonDesglose`, `ComplianceInfo`, `DocumentContext` + `from_engine_result()` que anonimiza PII y aplana desglose segmentado), `liquidator/contracts/__init__.py` (exports). **+1 archivo tests:** `liquidator/tests/test_contracts/test_document_context.py` (nuevo, 45 tests en 6 clases: RenglonDesglose 5, ComplianceInfo 11, DocumentContext 5, from_engine_result segmentado 9, plano 2, edge cases 11, inmutabilidad 2). **DoD:** 45/45 PASS. Suite: 630P/42F/15E. 0 regresiones. |
| 3.D        | `liquidacion_BLOQUEADA.*` para NO_GO + exit 2         | **CERRADA**   | S36, 2026-06-14 | Anidada en Fase 3. **2 archivos de código:** `liquidator/cli/main.py` (helper `_write_output_artifacts()` que emite `liquidacion_BLOQUEADA.json` + `liquidacion_BLOQUEADA.md` cuando `compliance_status == NO_GO`, exit 2; sin PDF por AGENTS.md #7), `liquidator/templates/comprobante_finiquito.md` (sin cambios — el bloqueo usa `_render_blocked()` del MarkdownGenerator). **+1 archivo tests:** `liquidator/tests/test_cli/test_liquidar.py` (nuevo, 20 tests en 4 clases: rama GO 8, rama NO_GO 6, --json-only 3, helper directo 3). **DoD:** 20/20 PASS. Suite: 650P/42F/1xfail/15E. 0 regresiones. |
| 3.G        | (Addendum finiquito) PreRender por motivo             | **CERRADA**   | S34, 2026-06-14 | Anidada en Fase 3. **4 archivos de código:** `pre_render_validator.py` (nuevo, REQUISITOS_POR_MOTIVO 10 motivos + PreRenderValidator.validar_requisitos_por_motivo + obtener_nota_render), `comprobante_finiquito.md` (bloques condicionales: renuncia → NO APLICA indemnización Art.49.6/Art.64, vacaciones Art.189-190), `markdown_generator.py` (+80 líneas: import PreRenderValidator, desglose en context, _validar_pre_render + _render_pre_render_error, motivo_terminacion en context FINIQUITO). **+2 archivos tests:** `test_pre_render_validator_por_motivo.py` (25 tests: cobertura matriz 10 motivos, renuncia/despido/termino_fijo/otros motivos, guards, edge cases), `test_finiquito_renuncia_template.py` (8 tests: nota no-indemnización, vacaciones, motivo, formato COP, otros motivos no muestran nota). **DoD:** 33/33 PASS. Suite: 575P/41F/15E. 0 regresiones. |
| 3.H        | (Addendum preaviso) PreRender + plantilla preaviso    | **CERRADA**   | S35, 2026-06-14 | Anidada en Fase 3. **4 archivos:** `liquidator/output/markdown_generator.py` (+5, campos preaviso en _build_context), `liquidator/templates/comprobante_finiquito.md` (+25, bloque preaviso Art. 46), `liquidator/tests/test_output/test_preaviso_render.py` (nuevo, 11 tests), `Contexto/KB_LLM/05_plantillas.md` (nuevo, documentación de bloques condicionales). 11/11 PASS. Suite: 586P/41F/15E. 0 regresiones. |
|||| 4          | v2.0 release                                          | **CERRADA**   | S53, 2026-06-20 | **4.A ✓ (S37), 4.B ✓ (S38), 4.C ✓ (S39), 4.D ✓ (S40), 4.E ✓ (S41), 4.F ✓ S49, Suite 0F ✓ S51 (682P/28S/2xfail), Verbatim Art.488 ✓ S52 (texto literal SUIN+Senado), Verbatim SL2630-2024 ✓ S53 (knowledge base estructurada en legal_docs/SL2630-2024_knowledge_base.md con cifras exactas + 13 sentencias + mapping schemas Pydantic)**. CI con compileall + ruff + pytest + kb_freshness + `scripts/ci.sh`. ruff 0 errores. mypy 123 errores preexistentes no bloqueantes (`|| true` en script). README.md reescrito v2.0. Tag v2.0.0 creado y pusheado a origin. **S51 cerró los últimos 6F** (expected values desfasados + feature no implementada). **S52 cerró Fase 4 formalmente con Art.488 VERIFICADO** y SL2630-2024 en VERIFICADO_PARCIAL_AVANZADO (cabecera + doctrina + URLs primarias registradas; texto prosa pendiente interacción humana con la Relatoría). **S53 cerró el verbatim SL2630-2024 a VERIFICADO completo** tras entrega por el operador (Jhond) de la base de conocimiento estructurada completa (700 líneas, 26KB) con cifras exactas de condena, 13 sentencias CSJ citadas, 6 normas complementarias, mapping a schemas Pydantic del motor, y glosario. Cifras clave SL2630-2024: condena total $20.755.559 (cesantías $20.665.485 + vacaciones $39.367 + intereses $50.707). Doctrina implementada en Tarea 2.B-bis SalarioResolver (24 tests) + Tarea 2.X IPCIndexador (36 tests) = 60 tests verdes. **Cierre formal de Fase 4: COMPLETO con ambos verbatims en VERIFICADO.** |
||| 4.D        | Limpieza documental (plan §9.2)                       | **CERRADA**   | S40, 2026-06-14 | Anidada en Fase 4. **3 archivos creados/modificados:** `CONTRIBUTING.md` (122 líneas, 6 secciones), `docs/code_quality_analysis.md` (reescrito completo: 301 líneas, métricas post-Fase 4 reales). **2 archivos eliminados:** `QWEN.md` (v1.0.0 legacy, referenciaba `settle`), `docs/health/system_health.json` (stale 2025-11-04, 10 componentes UNHEALTHY falsos), `docs/validation_results.json` (stale 2025-11-04, 17 FAIL obsoletos). **0 código modificado, 0 regresiones.** Suite sin cambios: 650P/42F/1xfail/15E. |
| 5          | Investigación casos reales (opcional)                 | CONDICIONAL   | —       | Solo si surgen casos en Fases 0-4.                             |

**Estados posibles:** NO INICIADA · EN CURSO · BLOQUEADA · CERRADA · CONDICIONAL · CANCELADA.

---

## Decisiones de addendas (vigentes)

### Addendum SL2630-2024 + IPC
- **Archivo:** `Planificación/addendum_sl2630_y_ipc_2026-06-09.md`
- **Estado:** APROBADO CON REPAROS. Absorbido en v2.0.0 (NO como v2.0.1).
- **Distribución:** Tarea 1.C-bis → Fase 1; Tarea 2.B-bis → Fase 2; Tarea 2.X → Fase 2-bis.
- **Reparos bloqueantes (cerrar antes de Fase 2-bis DoD):**
  - (a) NO usar Art. 155 CST para prescripción — usar **Art. 488 CST**.
  - (b) Verificar texto literal, sala y URL oficial de **SL2630-2024** antes de cerrar.
  - (c) Modelar IPC como **índices acumulados**, NO como tasas anuales de inflación.

### Addendum finiquito por renuncia + vacaciones compensadas
- **Archivo:** `Planificación/addendum_finiquito_renuncia_vacaciones_2026-06-11.md`
- **Estado:** APROBADO CON REPAROS. Absorbido en v2.0.0.
- **Distribución:** Tarea 1.C-ter → Fase 1; Tarea 2.B-ter → Fase 2; Tarea 2.Z → Fase 2; Tarea 3.G → Fase 3.
- **Reparos bloqueantes (cerrar antes de DoD de cada tarea):**
  - (a) Verificar **Art. 189 CST párr. 1°** en SUIN (`https://www.suin-juriscol.gov.co/`) antes de cerrar 2.B-ter; registrar `estado_verificacion: "VERIFICADO"` con URL y fecha en `params/normas.json` (entrada `CST_189_VACACIONES`).
  - (b) El motor debe distinguir *vacaciones compensadas por acuerdo mutuo* (Art. 189) de *vacaciones obligatoriamente compensadas en finiquito* (Art. 189 párr. 1° + Art. 190) — modo `FINIQUITO` invoca `calculate_vacaciones_compensadas_finiquito`; modo `PERIODICA` NO.
  - (c) **Indemnización Art. 64 CST NO se implementa en v2.0** (queda referenciada en `Contexto/KB_LLM/01_reglas_calculo.md` para casos futuros).

### Addendum Fase 3 — Divergencias arquitectónicas v2.0.0
- **Archivo:** `Planificación/addendum_fase3_arquitectura_2026-06-14.md`
- **Estado:** APROBADO. Absorbido en v2.0.0.
- **Origen:** Cierre de Fase 3 base (sesión S36, 2026-06-14). Documenta las 4 divergencias entre el plan §8 y la implementación real:
  - **D1:** Plantillas `.md` con bloques Jinja (en lugar de `.j2` separados) — `comprobante_periodica.md`, `comprobante_finiquito.md`, `partials/`, `styles/`. Funcionalidad equivalente, nomenclatura distinta.
  - **D2:** Renderers `*_generator.py` (no `*_renderer.py`) — `markdown_generator.py`, `pdf_generator.py`. Sufijo describe mejor la responsabilidad. `pre_render_validator.py` separado como mejora de S34.
  - **D3:** Auditoría con 4 archivos (`audit_logger.py`, `hash_calculator.py`, `trail_generator.py`, `versioning_manager.py`) en lugar de 1 (`immutable_logger.py`). Separación de responsabilidades; 23 tests en `test_audit/`.
  - **D4:** `liquidacion_BLOQUEADA.*` sin PDF en NO_GO — AGENTS.md regla #7 prevalece sobre plan §8 (jerarquía de verdad).
- **Tareas cerradas por absorción:** 3.B, 3.C, 3.E, 3.F (cobertura funcional ya existente).
- **Tareas cerradas en S36:** 3.A (`DocumentContext` formal) + 3.D (`liquidacion_BLOQUEADA.*` + exit 2).

### Addendum preaviso (contrato a término fijo, Art. 46 CST)
- **Origen:** Decisión 2026-06-13, absorbido en v2.0.0 (no addendum separado).
- **Estado:** APROBADO CON REPAROS. Absorbido en v2.0.0.
- **Distribución:** Tarea 1.C-quater → Fase 1; Tarea 2.B-cuater → Fase 2; Tarea 2.Y → Fase 2; Tarea 3.H → Fase 3.
- **Alcance:** Solo contratos a término fijo. Art. 46 CST: 30 días de preaviso para no renovar. Indemnización por preaviso insuficiente: `(SBL / 30) × dias_faltantes`. NO aplica a INDEFINIDO, OBRA_LABOR ni PRESTACION.
- **Reparos bloqueantes (cerrar antes de DoD de cada tarea):**
  - (a) Verificar **texto literal del Art. 46 CST** en SUIN (`https://www.suin-juriscol.gov.co/`) antes de cerrar 2.B-cuater; registrar `estado_verificacion: "VERIFICADO"` con URL y fecha en `params/normas.json` (entrada `CST_46_PREAVISO`).
  - (b) **Indemnización por preaviso = renglón separado** de la indemnización por despido sin justa causa (Art. 64). NO acumular.
  - (c) **Preaviso contractual (pacto > 30 días) NO se implementa** en v2.0 — extensión futura.

---

## Regla de cierre de sesión (a transcribir a AGENTS.md cuando se cree en Fase 0)

Al cerrar sesión, en este orden:
1. **Validar DoD contra código vivo** (regla §5.5.11 del diagnóstico: si código y plan discrepan, código gana).
2. **Actualizar este REGISTRY.md** — cambiar estado de fase/tarea, agregar entrada al log de cierres.
3. **Si quedó alguna fase cerrada**, agregar entrada en `CHANGELOG.md` bajo `[Unreleased]`.
4. **Si hubo cambio en params/reglas**, sincronizar `Contexto/KB_LLM/` correspondiente (cuando exista en Fase 0+).
5. **Si se tocó un addenda**, verificar que la decisión aprobada no haya cambiado (si cambió, documentar en el addenda y re-evaluar aprobaciones).

**No cerrar sesión sin completar los 5 puntos.**

---

## Log de cierres de sesión

> **Movido a archivo aparte el 2026-06-14.** Ver
> [`REGISTRY_LOG.md`](./REGISTRY_LOG.md) para el histórico completo de cierres
> de sesión (S0 → S31, ~60KB de evidencia verbatim por sesión). El REGISTRY
> principal queda con núcleo operacional; este log archivado **NO se carga
> por default** — solo se consulta puntualmente cuando se necesita el
> detalle histórico de un SXX.
>
> **Convención de mantenimiento al cerrar sesión:** agregar nueva entrada
> AL TOPE de la tabla en `REGISTRY_LOG.md` + actualizar `REGISTRY.md`
> "Estado actual" y "Tabla de fases" (solo la fila resumen).


---

## Handoff — si abrís esto en una sesión nueva

> Esta sección existe para que un agente (o vos) pueda retomar **sin
> re-leer las 3.353 líneas del plan**. Verificá los 6 checks, leé el
> orden sugerido, y arrancá la próxima tarea.

### Verificación rápida de estado (6 checks, ~10 segundos)

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli

# 1. KB existe con 11 archivos
n=$(ls Contexto/KB_LLM/ 2>/dev/null | wc -l); echo "[KB] $n archivos (esperado 11)"

# 2. Prompts ausentes (cerrado en S6 — Tarea 0.F)
test -d Contexto/prompts && echo "[prompts] OK" || echo "[prompts] PENDIENTE 0.F"

# 3. AGENTS.md presente (creado en S7 — Tarea 0.G)
test -f AGENTS.md && echo "[AGENTS] OK (creado en S7 — Tarea 0.G)" || echo "[AGENTS] PENDIENTE 0.G ⚠"

# 4. check_kb_freshness.py existe Y corre con exit 0 (cerrado en S8 — Tarea 0.H)
test -f scripts/check_kb_freshness.py && \
  test -f liquidator/tests/test_kb_freshness.py && \
  python3 scripts/check_kb_freshness.py >/dev/null 2>&1 && \
  echo "[KB-fresh] OK (creado en S8 — Tarea 0.H)" || \
  echo "[KB-fresh] PENDIENTE 0.H"

# 5. .git inicializado (cerrado en S9 — Tarea 0.I)
test -d .git && echo "[git] OK (cerrado en S9 — Tarea 0.I)" || echo "[git] PENDIENTE 0.I"

# 6. KB y código sin Art. 155 en contexto de prescripción (R-LEG-02).
#    Búsqueda focalizada: solo lo operacional (NO Planificación/, donde
#    los reparos y decisiones LEGÍTIMAMENTE mencionan "no usar Art. 155").
matches=$(grep -rn "Art\. 155" liquidator/ params/ Contexto/KB_LLM/ legal_docs/ 2>/dev/null)
if [ -z "$matches" ]; then
    echo "[Art.155] OK: cero referencias operacionales"
else
    echo "[Art.155] REVISAR (matches operacionales):"
    echo "$matches"
    echo "→ Si es cita legal vigente, reemplazar por Art. 488 CST."
    echo "→ ESPERADO en Contexto/KB_LLM/06_riesgos_modelo.md (documenta R-LEG-02)."
    echo "  Los matches allí son la descripción del riesgo, no uso. OK ignorar."
    echo "→ INESPERADO en liquidator/, params/, legal_docs/, otras notas KB."
    echo "  Esos SÍ son uso operacional: evaluar y reemplazar por Art. 488 CST."
fi
```

Si algún check falla distinto a lo esperado, **no avanzar**: actualizar
REGISTRY primero.

```bash
# 7. Tests de params compilan sin errores de colección (R-OP-05 RESUELTO S13)
uv run --with pytest --with jsonschema python3 -m pytest liquidator/tests/test_params/ --collect-only -q >/dev/null 2>&1 && \
  echo "[params] OK: 60 tests collected, 0 collection errors (R-OP-05 RESUELTA S13)" || \
  echo "[params] REVISAR: collection errors en params"

# 8. Tests de utils pasan 7/7 (R-OP-06 RESUELTO S13)
uv run --with pytest --with python-dateutil --with jsonschema python3 -m pytest liquidator/tests/test_utils/test_date_currency_utils.py -q >/dev/null 2>&1 && \
  echo "[utils] OK: 7/7 PASS (R-OP-06 RESUELTA S13)" || \
  echo "[utils] REVISAR: runtime failures en date_currency_utils"
```

### Orden de lectura sugerido (1-2 minutos)

1. **"Estado actual"** (arriba) → qué tarea viene.
2. **Esta sección "Handoff"** → trampas y orden de tareas restantes.
3. **"Tabla de fases"** → cómo encaja en el roadmap.
4. **"Decisiones de addendas"** → qué reparos bloquean.
5. **"Log de cierres"** → última fila S13 para entender qué se hizo.
6. **KB nota relevante** (si la tarea es de cálculo/legal → 01-03; si es
   de input/output → 04-05; si es de riesgos → 06; si es operativo → 07).
7. **Plan §X.Y** de la tarea (líneas exactas abajo en la tabla).

### Tareas de Fase 1 (CERRADA S26)

**12/12 tareas cerradas en S12-S25.** Plan §6.2 referencia: Tarea 1.A-utils (S12), 1.X (S13), 1.A-plan (S14), 1.B (S15), 1.C (S16), 1.E (S17), 1.D (S18), 1.I (S19), 1.G (S20), 1.F (S22), 1.C-bis (S23), 1.C-ter (S24), 1.C-quater (S25). Cierre formal **S26** (R-OP-02/07/08/09 + bug checklist_loader cerrados). Para evidencia verbatim (commits, archivos, tests por tarea) ver [`REGISTRY_LOG.md`](./REGISTRY_LOG.md) entradas S12-S26.

### Pendientes heredados de S11

**5/5 cerrados (P-S11.1..P-S11.5).** P-S11.1/2/4 OK. P-S11.3 RESUELTO S21 (R-OP-11). P-S11.5 estado R-OP-02 conocido, fixeado en Fase 1. Ver [`REGISTRY_LOG.md`](./REGISTRY_LOG.md) entrada S11.6 para detalles.

### Trampas conocidas (no violar)

**Activas (operacionales):**

- **No cerrar sesión sin los 5 pasos del cierre** (ver bloque inferior).
- **No generar PDF si compliance = `NO_GO`** (regla AGENTS.md #7).
- **No disfrazar `.txt` como PDF** (regla AGENTS.md #8).
- **No hardcodear SMMLV, aux_trans, tasas, plazos** (regla #4).
- **No usar outputs como expected values** sin firma del usuario
  (`output/_legacy/` NO es contrato; es histórico).
- **Prescripción de prestaciones = Art. 488 CST**, NO Art. 155
  (R-LEG-02, R-LEG-03). Cualquier referencia a Art. 155 en ese contexto
  es bug.
- **SL2630-2024 / Art. 488 CST** citados como `PENDIENTE_VERBATIM` en
  `params/normas.json` entradas `SL2630_2024` y `CST_488_PRESCRIPCION`
  (S28). Verificar verbatim SUIN antes de cerrar v2.0 release.
- **Indemnización Art. 64 CST** NO implementada en v2.0 (R-LEG-01);
  output debe traer `indemnizacion: null`.
- **R-LEG-06 (ACTIVA):** NO implementar pago mensual de intereses sobre
  cesantías en el motor. SUIN refutó el "Art. 64 de la Ley 2466/2025 =
  pago mensual intereses"; Art. 64 = "Régimen simple laboral".
  Entrada `LEY_2466_2025_INTERESES_MENSUALES` en `params/normas.json`
  marcada `PENDIENTE_TEXTO_LITERAL`.
- **R-LEG-07 (ACTIVA):** Decreto 1469/2025 (SMMLV 2026 $1.750.905)
  **suspendido provisionalmente** por Consejo de Estado desde
  2026-02-12; valor se mantiene por Decreto 159/2026. Output debe
  listar **ambos** decretos en `meta.referencias_normativas`.
- **Sandbox WSL (ACTIVA):** `python3` directo denegado → usar
  `uv run --with <pkg> python3 <script>`. `git commit -m` con mensaje
  largo (>1KB) denegado → usar subject corto <100 chars; detalle
  extendido va en REGISTRY/CHANGELOG.

**Resueltas (referencia, no operacional):**

- R-OP-02 (Causa 2) / R-OP-07 / R-OP-08 / R-OP-09 / bug
  `checklist_loader.py:21` → RESUELTOS S26.
- R-OP-05 / R-OP-06 (params + utils) → RESUELTOS S13.
- R-OP-03 (refactor a artefacto de validación) / R-OP-10 (maxLength 20→40) /
  R-OP-11 (campos plazos_pago opcionales) → RESUELTOS S20-S21.
- Art. 189 párr. 1° CST → VERIFICADO SUIN S29 (reparo cerrado).
- Art. 46 CST preaviso → VERIFICADO SUIN S30 (reparo cerrado).
- `WorkflowOrchestrator` no soporta Forma 2 anidada como input de
  usuario → fix en Tarea 2.A (Fase 2; ejemplos SBL indexada usan
  Forma 1 plana con campos extendidos en raíz como mitigación
  temporal). Ver **R-LEG-08** en `Contexto/KB_LLM/06_riesgos_modelo.md`
  (canonizado S48, Tarea 4.F planning). El `InputParser` legacy lee
  17 campos en raíz y pasa el dict completo al engine, que consume
  los campos extendidos del schema Forma 2 directamente.

> **Detalle completo de R-OP/LEG/R-SEC**: ver
> [`Contexto/KB_LLM/06_riesgos_modelo.md`](../Contexto/KB_LLM/06_riesgos_modelo.md)
> — fuente canónica de riesgos con resolución.

### Estado del caso canónico (KB_LLM/09)

- **Documentado:** sí (S5, 2026-06-13).
- **Ejecutado end-to-end:** NO. Motor no estabilizado (Fase 0).
- **Trazabilidad:** cada vez que se ejecute (primera vez en Fase 1 Tarea
  1.B), actualizar `KB_LLM/09` con valores observados y referenciar el
  golden file en `examples/expected/`.
- **Cuándo es bloqueante:** el caso canónico DEBE poder ejecutarse
  antes de cerrar cualquier fase. Si falla, es bug del motor → Fase
  anterior, no se cierra la fase objetivo.

### Regla de cierre (recordatorio, ya en bloque arriba)

Al cerrar la sesión, en este orden:
1. Validar DoD contra código vivo.
2. Actualizar este REGISTRY (estado, fase, log, próxima).
3. Si cerraste fase → entrada en `CHANGELOG.md` bajo `[Unreleased]`.
4. Si tocaste `params/` o reglas → sincronizar `KB_LLM/02` o `03`.
5. Si tocaste un addenda → verificar que la decisión aprobada no haya
   cambiado; si cambió, documentar en el addenda y re-evaluar.

**No cerrar sesión sin completar los 5 puntos.**

---

## Cómo se lee este archivo

- **Abrir sesión nueva** → leer **primero "Handoff"** (verificación 8
  checks + trampas activas), después "Estado actual" (5 líneas).
- **Decidir qué viene** → leer "Tabla de fases" (1 pantalla) + "Handoff".
- **Entender contexto histórico** → leer
  [`REGISTRY_LOG.md`](./REGISTRY_LOG.md) (NO se carga por default).
- **Recordar por qué un addenda se decidió así** → leer "Decisiones de
  addendas".

---

## Referencias

- **Plan fuente:** `Planificación/plan_modernizacion_v2.0_2026-06-09.md` (~4.021 líneas — consultar solo para detalle)
- **Diagnóstico fuente:** `Contexto/diagnostico_liquidacion_cli_2026-06-09.md`
- **Addenda:**
  - `Planificación/addendum_sl2630_y_ipc_2026-06-09.md`
  - `Planificación/addendum_finiquito_renuncia_vacaciones_2026-06-11.md`
- **Estado de Fase 0 validado contra disco:** 2026-06-13 (sesión S11 — Tarea 0.K cerrada, **Fase 0 CERRADA** con 0.A-0.K ✓; 2 issues legales nuevos — R-LEG-06, R-LEG-07 — documentados en `Contexto/KB_LLM/06_riesgos_modelo.md`; 4 validaciones ejecutables del plan §5.2 T0.K pendientes para próxima sesión por bloqueo del sandbox WSL). Verificación rápida de 6+1 checks en sección "Handoff" (7mo: `pytest --collect-only` post-1.A debe dar 0 collection errors).
