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

- **Última sesión cerrada:** **S31 — 2026-06-14, Tarea 2.Y (addendum preaviso): Compliance preaviso Art. 46 CST — CERRADA**. **3 archivos de código + 1 soporte.** (1) `params/checklist.json` — V012 (V_PREAVISO_TERMINO_FIJO) + V013 (V_PREAVISO_DECLARADO) agregados, severity MEDIUM, non-blocking. 13 reglas totales V001-V013. (2) `liquidator/compliance/rule_evaluator.py` — mapping V012/V013 en `build()`, funciones `_v012_preaviso_termino_fijo` (valida datos de cálculo para FINIQUITO+FIJO+vencido: dias_preaviso o fechas, PASS si >=30d, WARN si <30d con referencia a reparo b) y `_v013_preaviso_declarado` (defensa en profundidad: valida consistencia de preaviso_entregado/fecha_preaviso, FAIL si vencido sin declarar o True sin fecha, WARN si False, captura drift de bypass Pydantic). Fallback para Forma 1 plana: `or not contrato` en guard. (3) `liquidator/tests/test_compliance/test_preaviso_compliance.py` (nuevo, 27 tests): 4 clases (V012 11, V013 9, integración ComplianceEngine 4, reparos addendum 3). **+1 soporte:** `Contexto/KB_LLM/03_compliance_blocking.md` — tabla V011-V013. **Tests:** 27/27 PASS. Suite: 524 passed / 36 failed / 15 errors (+27 vs S30 baseline). 0 regresiones. **Pitfall detectado:** `input_data.get("contrato", {})` devuelve `{}` vacío (no None) cuando no hay contrato anidado — fix: `or not contrato` en fallback. **Fase 2 activa.** Tarea 2.Y CERRADA.
- **Próxima tarea a ejecutar (post-S31):** **Fase 2 activa.** Tarea 2.Y (Compliance preaviso Art.46) CERRADA. Próximas opciones: 2.Z (Compliance vacaciones), 3.G (PreRender por motivo), 3.H (PreRender preaviso). 2.Z complementa compliance de vacaciones; 3.G/3.H son Fase 3. A elección del usuario.
- **Bloqueos activos:** ninguno de Fase 0 (cerrada). PENDIENTE (pospuesto por usuario en S3): eliminación de `__pycache__/`, `htmlcov/`, `.coverage`, `liquidacion_nomina_colombia.egg-info/`, `documentos_legales_rurales/` (vacío). **Issue resuelto post-S26:** `.env.backup*` del .gitignore ahora SÍ matchea — `.gitignore` reescrito sin inline comments (R-OP-09 cerrado). **Issue post-S10:** `pytest` con `uv run --with pytest …` SÍ funciona en WSL. **Issue post-S11:** `python3` directo denegado por sandbox — mitigación: `uv run --with <pkg> python3 <script>`. **Issue legal post-S11:** nulidad del Decreto 1469/2025 pendiente (R-LEG-07) — SMMLV 2026 vigente por D. 159/2026; vigilar antes de v2.0 release.

---

## Tabla de fases

| Fase       | Título                                                | Estado        | Cerrada | Pendiente / Notas                                              |
|------------|-------------------------------------------------------|---------------|---------|----------------------------------------------------------------|
| 0          | Higiene + segundo cerebro mínimo                      | **CERRADA**   | S11, 2026-06-13 | 0.A-0.K ✓ (orden estricto cumplido: 0.A→0.B→…→0.K). DoD completo: KB 10/10, params 2025+2026 vigentes, normas con URLs SUIN reales, script freshness year-aware, suite inventariada (75 issues → Fase 1). |
| 1          | Estabilizar y formalizar                              | **CERRADA**   | S26, 2026-06-13 | **12/12 tareas ✓, todos los R-OP cerrados.** (Tarea 1.A-utils S12, 1.X S13, 1.A-plan S14, 1.B S15, 1.C S16, 1.E S17, 1.D S18, 1.I S19, 1.G S20, **R-OP-11 S21**, **1.F S22**, **1.C-bis S23**, **1.C-ter S24**, **1.C-quater S25**). R-OP-02 Causa 2 S26, R-OP-07 S26, R-OP-08 S26, R-OP-09 S26, bug checklist_loader.py S26. 393 passed / 36 failed / 15 errors (36 fails preexistentes asignados a Fase 2+). Fase 1 CERRADA formalmente. |
| 1.C-bis    | (Addendum SL2630) Schema `Salario` extendido          | **CERRADA**   | S23, 2026-06-13 | Anidada en Fase 1. Aditiva retrocompatible. **3 archivos:** `liquidator/contracts/input_model.py` (MesValor + sbl_por_anio + historial_salarial + model_validator), `liquidator/tests/test_contracts/test_salario_extendido.py` (nuevo, 10 tests), `Contexto/KB_LLM/04_schema_entrada.md`. **DoD:** 10/10 PASS, 39/39 PASS en test_contracts, 11/11 PASS caso canónico. Motor NO consume nuevos campos en Fase 1; Tarea 2.B-bis (Fase 2) los activará vía `SalarioResolver`. |
| 1.C-ter    | (Addendum finiquito) Schema `Contrato` + `Vacaciones` | **CERRADA**   | S24, 2026-06-13 | Anidada en Fase 1. Aditiva retrocompatible. **4 archivos:** `liquidator/contracts/input_model.py` (MotivoTerminacion enum 10 valores, PeriodoDisfrute, VacacionesEstado, Contrato actualizado, LiquidacionInput actualizado), `liquidator/tests/test_contracts/test_vacaciones_estado.py` (nuevo, 15 tests), `liquidator/tests/test_contracts/test_motivo_terminacion.py` (nuevo, 15 tests), `Contexto/KB_LLM/04_schema_entrada.md`. **DoD:** 69/69 PASS en test_contracts, 11/11 PASS caso canónico. Motor NO consume los nuevos campos en Fase 1; Tarea 2.B-ter (Fase 2) usará motivo_terminacion y vacaciones tipadas. |
| Tarea 1.C-quater | (Addendum preaviso) Schema `Contrato` preaviso Art.46 | **CERRADA**   | S25, 2026-06-13 | Anidada en Fase 1. Aditiva retrocompatible. **2 archivos:** `liquidator/contracts/input_model.py` (4 nuevos campos opcionales: `fecha_vencimiento_termino_fijo`, `preaviso_entregado`, `fecha_preaviso`, `dias_preaviso` + `model_validator _preaviso_consistencia` con 3 reglas: solo FIJO / `preaviso_entregado=True` exige `fecha_preaviso` / FINIQUITO+FIJO+vencido exige `preaviso_entregado` declarado), `liquidator/tests/test_contracts/test_preaviso_contrato.py` (nuevo, 16 tests en 4 clases: regresión canónica, reglas de éxito, reglas de fallo, consistencia), `Contexto/KB_LLM/04_schema_entrada.md` (marcado IMPLEMENTADO S25). **DoD:** 16/16 PASS en `test_preaviso_contrato.py`; 85/85 PASS en `test_contracts/`; 11/11 PASS caso canónico. 0 regresiones. Motor NO consume los nuevos campos en Fase 1; Tarea 2.B-cuater (Fase 2) los activará vía `IndemnizacionCalculator.calculate_indemnizacion_preaviso`. |
| 2          | Cálculo legal y motor correcto                        | **EN CURSO**  | —       | Fase 2 iniciada. 2.B-bis (S27) CERRADA. 2.X (S28) CERRADA. 2.B-ter (S29) CERRADA. 2.B-cuater (S30) CERRADA. 2.Y (S31) CERRADA. |
| 2.B-bis    | (Addendum SL2630) `SalarioResolver` SBL por año       | **CERRADA**   | S27, 2026-06-13 | Anidada en Fase 2. **4 archivos:** `liquidator/core/salario_resolver.py` (nuevo), `liquidator/core/workflow_orchestrator.py` (integración), `liquidator/core/__init__.py` (exports), `Contexto/KB_LLM/01_reglas_calculo.md` (SL2630-2024). **Tests:** 15 unitarios + 9 golden = 24/24 PASS. Suite: 417 passed (+24 vs S26). 0 regresiones. DoD: caso canónico verde, SBL variable produce cálculos distintos, 3 prioridades probadas. |
| 2.X        | (Addendum SL2630) Indexación IPC para prestaciones no pagadas | **CERRADA** | S28, 2026-06-13 | Anidada en Fase 2-bis. **8 archivos creados/modificados:** (1) `liquidator/calculators/indexacion.py` (nuevo) — clase `IPCIndexador` con validación defensiva anti-tasa, `from_json()` dual-formato, `indexar()` con ROUND_HALF_UP. (2) `liquidator/calculators/__init__.py` — export. (3) `liquidator/contracts/input_model.py` — modelo `PeriodoNoPagado` (4 fechas, 4 conceptos Literal, `model_validator` de consistencia causal). (4) `liquidator/compliance/rule_evaluator.py` — regla `V011` (V_INDEXACION_IPC, severity MEDIUM, no bloqueante) con prescripción Art. 488 CST. (5) `liquidator/core/engine.py` — `_procesar_periodos_no_pagados()` integrado en `process_input()`. (6) `params/normas.json` — `SL2630_2024` y `CST_488_PRESCRIPCION` (ambas `PENDIENTE_VERBATIM`). (7) `params/checklist.json` — `V011` con `formula`/`nota`. (8) `Contexto/KB_LLM/01_reglas_calculo.md` — sección "Indexación por IPC". **+4 archivos de soporte:** `params/ipc_variacion_anual_dane.csv` (17 años DANE), `params/ipc_dane_mensual.json` (204 índices mensuales base 100 en 2010-01), `scripts/build_ipc_index.py` (validador geométrico), `examples/inputs/prescripcion_indexada.json` + `examples/expected/prescripcion_indexada_result.json`. **Tests:** 24 unitarios (`test_indexacion.py`) + 12 golden (`test_prescripcion_indexada.py`) = 36/36 PASS. **Reparos cerrados:** (a) cero referencias a Art. 155 en `indexacion.py` (verificado por test), (c) defensa contra tasas disfrazadas. **Reparos pendientes (no bloquean DoD 2.X, sí bloquean v2.0 release):** (b) verificación verbatim SL2630-2024 y Art. 488 CST. **DoD plan §7-bis.1:** 9/9 checks cumplidos. |
| 2.B-ter    | (Addendum finiquito) Vacaciones compensadas           | **CERRADA**   | S29, 2026-06-13 | Anidada en Fase 2. **6 archivos de código:** `prestaciones_calculator.py` (+48 líneas, método `calculate_vacaciones_compensadas_finiquito` fórmula Art. 189-190 CST: `(SBL/30)×dias_pendientes`), `engine.py` (+68 líneas, hook `_calcular_vacaciones_si_finiquito` solo FINIQUITO), `test_vacaciones_finiquito.py` (nuevo, 9 tests), `test_finiquito_renuncia_212d.py` (nuevo, 8 tests), `finiquito_renuncia_212d.json` (fixture golden), `01_reglas_calculo.md` (sección vacaciones actualizada). **+2 archivos de soporte:** `params/normas.json` (entrada `CST_189_VACACIONES` con texto literal verificado SUIN, estado VERIFICADO). **Reparo (a) cerrado:** Art. 189 CST párr. 1° verificado verbatim en SUIN (num. 1: acuerdo mutuo; num. 2: compensación obligatoria al terminar). **Tests:** 17/17 PASS (9 unitarios + 8 golden). Suite: 470P/36F/15E. 0 regresiones. |
| 2.B-cuater | (Addendum preaviso) Indemnización preaviso Art.46 CST | **CERRADA**   | S30, 2026-06-14 | Anidada en Fase 2. Solo FINIQUITO + FIJO + vencido. **4 archivos de código:** `indemnizacion_calculator.py` (+85, método `calculate_indemnizacion_preaviso`), `engine.py` (+130, hook `_calcular_preaviso_si_fijo_vencido`), `test_preaviso.py` (nuevo, 18 tests), `test_preaviso_fijo_vencido.py` (nuevo, 10 tests golden). **+2 soporte:** `normas.json` (CST_46_PREAVISO VERIFICADO SUIN), `finiquito_fijo_vencido_preaviso.json` (fixture). **Reparos (a)(b)(c) cerrados.** Tests: 28/28 PASS (1 xfail). Suite: 497P/36F/15E. 0 regresiones. |
| 2.Z        | (Addendum finiquito) Compliance vacaciones            | NO INICIADA   | —       | Anidada en Fase 2.                                             |
| 2.Y        | (Addendum preaviso) Compliance preaviso Art.46 CST    | **CERRADA**   | S31, 2026-06-14 | Anidada en Fase 2. **3 archivos de código + 1 soporte.** `checklist.json` (V012+V013), `rule_evaluator.py` (+225, 2 funciones), `test_preaviso_compliance.py` (27 tests). Soporte: `03_compliance_blocking.md`. Tests: 27/27 PASS. Suite: 524P/36F/15E. 0 regresiones. |
| 2-bis      | IPC + anualización salarial (nueva)                   | NO INICIADA   | —       | Plan §7-bis. Requiere Fase 2.                                  |
| 3          | Documento generable robusto                           | BLOQUEADA     | —       | Requiere Fase 2.                                               |
| 3.G        | (Addendum finiquito) PreRender por motivo             | NO INICIADA   | —       | Anidada en Fase 3.                                             |
| 3.H        | (Addendum preaviso) PreRender + plantilla preaviso    | NO INICIADA   | —       | Anidada en Fase 3. Bloque condicional en finiquito.j2.         |
| 4          | v2.0 release                                          | BLOQUEADA     | —       | Requiere 0-3 + 3 liquidaciones reales verificadas.            |
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

# 1. KB existe con 10 archivos
n=$(ls Contexto/KB_LLM/ 2>/dev/null | wc -l); echo "[KB] $n archivos (esperado 10)"

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
- `WorkflowOrchestrator` no soporta Forma 2 anidada → fix en Tarea 2.A
  (Fase 2; ejemplos SBL indexada usan Forma 1 como mitigación temporal).

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
