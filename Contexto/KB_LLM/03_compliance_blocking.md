# 03 — Compliance: severidad, bloqueo y override

> El motor tiene 4 estados de compliance: `GO`, `WARN`, `NO_GO`,
> `OVERRIDE_APPROVED`. Esta nota explica la mecánica; los detalles de
> cada regla viven en `params/checklist.json`.

## Estados (semáforos)

| Estado              | Significa                                                           | ¿Bloquea generación? |
|---------------------|---------------------------------------------------------------------|----------------------|
| `GO`                | Todos los checks pasaron. Puede generarse liquidación.             | NO                   |
| `WARN`              | Hay warnings pero ningún check CRITICAL/HIGH falló.                | NO                   |
| `NO_GO`             | Al menos un check con `blocking: true` falló. NO debe generarse.   | **SÍ**               |
| `OVERRIDE_APPROVED` | Estado `NO_GO` con override humano registrado en auditoría.        | NO (con firma)       |

## Severidades (de `params/checklist.json`)

| Severity   | Comportamiento por defecto                                      |
|------------|------------------------------------------------------------------|
| `CRITICAL` | `blocking: true`. Falla → `NO_GO` salvo override.               |
| `HIGH`     | `blocking: true`. Igual que CRITICAL en v2.0.                    |
| `MEDIUM`   | `blocking: false`. Falla → `WARN`. No bloquea generación.        |
| `LOW`      | `blocking: false`. Falla → `WARN` informativo.                   |
| `INFO`     | Solo para auditoría; nunca falla.                               |

> **Decisión de producto v2.0 (diagnóstico §6.4):** HIGH bloquea igual
> que CRITICAL. Esto puede afinarse en Fase 4+ (release) si se decide
> que HIGH debe ser solo WARN.

## Reglas vigentes (extracto de `params/checklist.json`, v 2025-10-31)

| ID    | Descripción                                              | Severity   | Norma ref                       |
|-------|----------------------------------------------------------|------------|----------------------------------|
| V001  | Parámetros oficiales 2025 presentes y consistentes       | CRITICAL   | Decreto 1572/2024                |
| V002  | Contrato válido para liquidación de prestaciones         | CRITICAL   | Art. 23 CST                      |
| V003  | Auxilio transporte aplicado correctamente                | HIGH       | Checklist Auxilio Transporte Finca Rural + CST 161 |
| V004  | Fórmulas de cesantías correctas                          | CRITICAL   | Art. 249-250 CST                 |
| V005  | Intereses de cesantías con tasa legal vigente            | CRITICAL   | Ley 50/1990 Art. 99              |
| V006  | Prima semestre proporcional validada                     | MEDIUM     | Art. 306-308 CST                 |
| V007  | Vacaciones manejadas según modo de liquidación           | CRITICAL   | Arts. 186-192 CST                |
| V008  | Plazos de pago documentados                               | HIGH       | Art. 65 CST, Ley 50/1990 Art. 99 |
| V009  | (no leído en esta nota)                                   | ...        | ...                              |
|| V010  | (no leído en esta nota)                                   | ...        | ...                              |

> El archivo `params/checklist.json` tiene 13 reglas V001-V013. Esta
> tabla es extracto parcial; leer el archivo completo antes de
> modificar el motor.

Reglas V011-V013 (Fase 2):

| ID    | Descripción                                              | Severity   | Norma ref                       |
|-------|----------------------------------------------------------|------------|----------------------------------|
| V011  | Indexación IPC para prestaciones no pagadas              | MEDIUM     | SL2630-2024, Art. 488 CST        |
| V012  | Preaviso Art. 46 CST: FIJO vencido datos cálculo         | MEDIUM     | Art. 46 CST                      |
| V013  | Preaviso declarado: consistencia en FIJO                 | MEDIUM     | Art. 46 CST                      |

## Mecánica de ejecución (código vivo)

1. `liquidator/compliance/compliance_engine.py::ComplianceEngine.run(input_data, params, calculation_result, input_hash)`
   carga el checklist desde `liquidator/compliance/checklist_loader.py`.
2. Itera las reglas; para cada una, `rule_evaluator.py::RuleEvaluator.build(rule_id, rule_info)`
   construye un callable que evalúa el check.
3. Si `result == "PASS"` → incrementa `summary.passed`.
   Si `"WARN"` → `summary.warnings`. Si `"FAIL"` → `summary.failures` y,
   si `blocking: true`, agrega el rule_id a `blocking_failures`.
4. **Estado final:**
   - Si hay `blocking_failures` y `failures > 0` → `compliance_status = "NO_GO"`.
   - Si no, pero hay warnings → `WARN`.
   - Si no → `GO`.

## Override (`liquidator/compliance/override_manager.py`)

Un override convierte un `NO_GO` en `OVERRIDE_APPROVED` para permitir
generar el documento, dejando **registro inmutable** de auditoría.

- **Campos requeridos en input:** `human_override: true`, `operator_id` (≥3 chars), `override_reason` (≥10 chars).
- **Genera `OverrideRecord`** con `override_id` (UUID), `timestamp` (ISO),
  `operator_id`, `justification`, `compliance_checks_overridden` (lista
  de rule_ids), `original_status`, `new_status = "OVERRIDE_APPROVED"`,
  `input_hash`.
- **Persistencia:** en v2.0 cada override se acumula en memoria del
  proceso. En Fase 3 (auditoría inmutable) se persiste a
  `artifacts/override_log.jsonl` con hash encadenado.

## Pendientes para v2.0 (reparos bloqueantes)

- **Tarea 0.H** crea `scripts/check_kb_freshness.py` que también debe
  poder alertar si faltan checks o si una regla marcada como
  `blocking: true` no tiene `severity` CRITICAL o HIGH (consistencia
  schema).
- **Fase 2** (cierre de DoD) requiere: cap de cesantías con cita legal,
  `severity→blocking` activo en runtime, `OVERRIDE_APPROVED` integrado
  en CLI.
- **Reparo (b) addendum finiquito:** verificar Art. 189 CST párr. 1° en
  SUIN (`https://www.suin-juriscol.gov.co/`) antes de cerrar 2.B-ter;
  registrar `estado_verificacion: "VERIFICADO"` con URL y fecha en
  `params/normas.json` entrada `CST_189_VACACIONES` (entrada NUEVA, aún
  no creada).

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** lectura de `liquidator/compliance/compliance_engine.py`
  (61 líneas, mecánica documentada) y `liquidator/compliance/override_manager.py`
  (≥80 líneas, dataclass `OverrideRecord` documentada). Extracto de
  `params/checklist.json` (primeras ~50 líneas).
- **NO verificado:** el contenido completo de V009 y V010 ni el
  `checklist.json` versión 2025-10-31 al completo. Re-validar en
  Tarea 0.J o Fase 1.
