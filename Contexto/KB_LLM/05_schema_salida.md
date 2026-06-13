# 05 — Schema de salida (`liquidacion_result.json`)

> El motor produce un JSON de salida con shape fijo. El plan §3 (línea
> 156) define explícitamente que el formato de salida es el mismo que el
> del caso real histórico `liquidacion_pedro_franco.json` (hoy en
> `output/_legacy/`). Esta nota documenta ese shape y lo que cada
> sección debe contener en v2.0.

## Top-level (shape observado en casos históricos y plan §3)

```json
{
  "meta": {...},
  "trabajador": {...},
  "parametros": {...},
  "desglose": {...},
  "total_liquidacion": int,
  "validaciones_y_alertas": {...},
  "normas_aplicadas": [...],
  "compliance_report": {...}
}
```

## `meta` — Metadatos de la ejecución

Campos esperados:

| Campo                              | Tipo   | Notas                                                   |
|------------------------------------|--------|---------------------------------------------------------|
| `modo`                             | str    | `PERIODICA` \| `FINIQUITO`.                             |
| `fecha_generacion`                 | ISO dt | Timestamp de la corrida.                                |
| `motor_version`                    | str    | Versión semántica del motor (target: 2.0.0).           |
| `input_hash`                       | str    | SHA256 del input completo (trazabilidad).               |
| `output_hash`                      | str    | SHA256 del JSON de salida (Fase 3).                     |
| `parametros_por_segmento`          | object | **Crítico para auditoría multi-año.** Ver abajo.        |
| `plantilla_version`                | str    | Versión de la plantilla Jinja usada (Fase 3).          |
| `compliance_status`                | str    | `GO` \| `WARN` \| `NO_GO` \| `OVERRIDE_APPROVED`.       |

`parametros_por_segmento` debe verse así para el caso canónico:

```json
{
  "parametros_por_segmento": {
    "2025": {"params_version": "2025-10-31", "rango": "2025-11-16 → 2025-12-31", "dias": 46, "params_ref": "params/2025.json"},
    "2026": {"params_version": "2026-06-09", "rango": "2026-01-01 → 2026-06-09", "dias": 160, "params_ref": "params/2026.json"}
  }
}
```

> Esto NO es un único `params_version`: cada segmento debe registrar
> su `params_version` por separado. El bug clásico es reportar solo
> el último `params_version` aplicado, perdiendo la trazabilidad del
> segmento 2025.

## `trabajador` — Eco del input (anonimizado en KB y logs)

Eco literal del input. En logs y en la KB debe aparecer
`[ANONIMIZADO]`. En el archivo de salida real, los datos van
textuales (es la liquidación que el usuario va a entregar / archivar).

## `parametros` — Params resueltos al momento de cálculo

Eco de los `params/<año>.json` que se aplicaron. **No** incluir
secretos ni claves. En v2.0 se incluye el árbol completo del JSON
anual (SMMLV, AUXILIO_TRANS, LIMITE_AUXILIO, TASA_INT_CESANTIAS,
DIAS_BASE, VACACIONES_DENOM, REDONDEO, TOPE_INDEMNIZACION_SMMLV,
FECHA_APLICACION_RECARGO_DOMINICAL, version, referencia).

## `desglose` — Conceptos liquidados, agrupados por año

**Cada año calendario es un sub-objeto**, no un campo plano.
Estructura esperada:

```json
{
  "desglose": {
    "2025": {
      "cesantias": int,
      "intereses_cesantias": int,
      "prima": int,
      "vacaciones": int,
      "indemnizacion": null,
      "recargo_dominical": int
    },
    "2026": {
      "cesantias": int,
      "intereses_cesantias": int,
      "prima": int,
      "vacaciones": int,
      "indemnizacion": null,
      "recargo_dominical": int
    }
  }
}
```

> **Convención:** `indemnizacion: null` cuando NO aplica (caso
> PERIODICA sin despido). En v2.0 NO se calcula (ver
> `01_reglas_calculo.md` y `06_riesgos_modelo.md` R-LEG-01).

## `total_liquidacion` — Suma bruta

Entero en pesos. Se computa como `sum(desglose[*][*])`. Sin
descuentos de seguridad social ni retención en la fuente (fuera de
alcance v2.0).

## `validaciones_y_alertas` — Warnings y errores no bloqueantes

Sub-objeto con listas:

```json
{
  "validaciones_y_alertas": {
    "warnings": [...],
    "info": [...]
  }
}
```

Ejemplos de warnings esperados en el caso canónico:
- `W-CAP-CESANTIAS-2026`: "SBL supera el tope de aux_trans del año 2026 (3.501.810), auxilio de transporte no aplicado." (En el caso canónico SBL=2.200.000, no aplica).
- `W-IPC-PRESCRIPCION`: pendiente de implementación; placeholder.

## `normas_aplicadas` — Lista de citas legales usadas

Array de objetos con la estructura de `params/normas.json` (id,
nombre, url, texto_relevante). Sirve para que el documento PDF/MD
final pueda mostrar "según Ley 50/1990 Art. 99" en cada renglón.

Para el caso canónico (modo PERIODICA, 206 días), las normas
mínimas son:
- `LEY50_99` (intereses).
- `CST_249_252` (cesantías).
- `CST_306_308` (prima).
- `CST_186_192` (vacaciones, base).
- `DECRETO_1572_2024`, `DECRETO_1573_2024` (params 2025).
- `DECRETO_1469_2025`, `DECRETO_1470_2025` (params 2026).
- `LEY_2466_2025` (recargo dominical fase vigente).

## `compliance_report` — Eco del `compliance_engine.py::run`

Sub-objeto con `compliance_status`, `summary {passed, warnings,
failures}`, `checks[]` (cada uno con id, result, blocking, evidence,
norma), `blocking_failures[]`, `input_hash`, `output_hash`,
`params_version`. Ver `03_compliance_blocking.md`.

## Artefactos derivados (Fase 3)

A partir del JSON se generan (en Fase 3, no en v2.0 base):

- `liquidacion_<caso>.md` — vista humana para revisión.
- `liquidacion_<caso>.pdf` — documento final. Si compliance es
  `NO_GO` sin override, se genera `liquidacion_<caso>_BLOQUEADA.*`
  con explicación (regla AGENTS.md #7: "No generar PDF si el estado
  de compliance es `NO_GO`").
- `artifacts/audit/<caso>_<timestamp>.json` — copia inmutable con
  hash encadenado.

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** shape documentado en plan §3 línea 156 y nombres
  de campo en `output/_legacy/liquidacion_pedro_franco.json` y
  `compensacion_pedro_franco.json` (no leídos en detalle en esta
  sesión; existencia verificada en Tarea 0.C, S3).
- **NO verificado:** que el código actual (`liquidator/core/engine.py`
  o `workflow_orchestrator.py`) produzca exactamente este shape. La
  auditoría del shape se hace en Fase 1, Tarea 1.B (golden test del
  caso canónico).
