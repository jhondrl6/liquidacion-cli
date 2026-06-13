# 04 — Schema de entrada (qué recibe el motor)

> El motor acepta dos formas de input: (1) **input informal** vía
> `examples/inputs/*.json` (lo que el usuario escribe a mano), y (2)
> **input segmentado** (lo que el orquestador produce internamente al
> cruzar año calendario). Esta nota documenta ambas y señala dónde el
> schema Pydantic formal se creará en Fase 1.

## Forma 1 — Input informal (lo que el usuario provee)

Ejemplo vigente: `examples/inputs/finca_rural.json` (10 líneas, modo
PERIODICA, contrato 2024-11-16 → 2025-11-15).

```json
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2024-11-16",
  "fecha_corte": "2025-11-15",
  "salario_mensual": 1800000,
  "reside_en_lugar_trabajo": true,
  "auxilio_conectividad": 150000,
  "comisiones_promedio_mensual": 200000,
  "tipo_contrato": "indefinido"
}
```

Campos observados:

| Campo                       | Tipo     | Obligatorio | Notas                                                       |
|-----------------------------|----------|-------------|-------------------------------------------------------------|
| `modo`                      | enum     | sí          | `PERIODICA` \| `FINIQUITO`. Mayúsculas.                     |
| `fecha_ingreso`             | ISO date | sí          | Formato `YYYY-MM-DD`.                                       |
| `fecha_corte`               | ISO date | sí          | `fecha_terminacion` real en FINIQUITO; as-of en PERIODICA.   |
| `salario_mensual`           | int      | sí          | En pesos colombianos, sin separador de miles.               |
| `reside_en_lugar_trabajo`   | bool     | no          | `true` desactiva aux_trans (Art. 161 CST).                  |
| `auxilio_conectividad`      | int      | no          ** | **No es aux_trans legal.** Verificar si se incluye en SBL.  |
| `comisiones_promedio_mensual` | int    | no          | Promedio últimos 6 meses. Se suma al SBL si `variable: true`. |
| `tipo_contrato`             | enum     | sí          | `indefinido` \| `fijo` \| `obra_o_labor` \| `ocasional`.    |

> **Inconsistencia detectada:** `auxilio_conectividad` aparece en el
> ejemplo de finca rural pero no hay claridad normativa sobre si entra
> al SBL. **Riesgo R-INP-01**, ver `06_riesgos_modelo.md`. La regla
> debe quedar explícita en el schema Pydantic de Fase 1 (Tarea 1.D).

## Forma 2 — Input segmentado (producido por el orquestador)

Para contratos que cruzan 1 de enero, el motor (vía
`liquidator/core/workflow_orchestrator.py`) genera una lista de
segmentos. **Este es el input "real" que llega a los calculadores.**

```json
{
  "modo": "PERIODICA",
  "trabajador": {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "empleador":  {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "contrato":   {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-09",
                 "tipo": "INDEFINIDO", "fecha_terminacion_real": null},
  "salario":    {"SBL": 2200000, "auxilio_transporte": false, "variable": false},
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31",
     "params_ref": "params/2025.json"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-09",
     "params_ref": "params/2026.json"}
  ]
}
```

Campos adicionales respecto a Forma 1:

| Campo                          | Tipo      | Obligatorio | Notas                                              |
|--------------------------------|-----------|-------------|----------------------------------------------------|
| `trabajador.nombre`            | str       | sí          | Anonimizar en KB y logs (`[ANONIMIZADO]`).         |
| `trabajador.documento`         | str       | sí          | Anonimizar; no escribir nunca el real.             |
| `empleador.nombre`             | str       | sí          | Anonimizar.                                        |
| `empleador.documento`          | str       | sí          | NIT anonimizado.                                   |
| `contrato.fecha_terminacion_real` | ISO date \| null | no | `null` en PERIODICA. Obligatorio en FINIQUITO.    |
| `salario.SBL`                  | int       | sí          | Resultado de `sbl_calculator.py`.                 |
| `salario.auxilio_transporte`   | bool      | sí          | Ya evaluado (no re-derivar).                       |
| `salario.variable`             | bool      | sí          | Si true, el SBL ya incluye promedio variable.      |
| `segmentos[]`                  | list      | sí          | 1 o más. Cada uno con `params_ref` resuelto.       |
| `segmentos[].anio`             | int       | sí          | Año calendario del segmento.                       |
| `segmentos[].desde`            | ISO date  | sí          | Inclusivo.                                         |
| `segmentos[].hasta`            | ISO date  | sí          | Inclusivo (convención día-a-día, ver §3 plan).     |
| `segmentos[].params_ref`       | path      | sí          | Path relativo al repo, ej. `params/2026.json`.     |

## Campos pendientes para Fase 1 (addenda)

- **Addendum finiquito (Tarea 1.C-ter):** añadir a `contrato`:
  - `motivo_terminacion` (enum: `RENUNCIA_VOLUNTARIA`, `DESPIDO_SIN_JUSTA_CAUSA`,
    `DESPIDO_CON_JUSTA_CAUSA`, `MUTUO_ACUERDO`, `EXPIRACION_CONTRATO`,
    `OTRO`).
  - `VacacionesEstado` (sub-objeto con `dias_pendientes`, `dias_compensados`,
    `dias_disfrutados_periodo_actual`).
- **Addendum SL2630 (Tarea 1.C-bis):** añadir a `salario`:
  - `sbl_por_anio` (dict `{anio: monto}`) para contratos multi-año
    con SBL variable. Por defecto el SBL es único (caso canónico), pero
    el motor debe aceptar la estructura anualizada.
  - `intereses_mensuales_acuerdo` (bool) para activar la variante
    Ley 2466/2025 Art. 64.

## Reglas de validación a la entrada

- `fecha_corte >= fecha_ingreso`.
- `salario_mensual > 0`.
- Si `modo == "FINIQUITO"`, `fecha_terminacion_real` debe estar set
  y ser >= `fecha_ingreso`.
- Si `reside_en_lugar_trabajo == true` y `auxilio_transporte == true`,
  el motor debe levantar `WARN` (inconsistencia) y continuar con
  `auxilio_transporte = false` (la norma `CST_161` prevalece sobre
  el input).
- Todos los campos monetarios son `int` (pesos), no `float`, para
  evitar drift de redondeo.

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** lectura de `examples/inputs/finca_rural.json` (10
  líneas, vigente) y del caso canónico documentado en plan §3
  (líneas 120-159).
- **NO verificado:** que `input_parser.py` realmente aplique la
  derivación a Forma 2. La forma 2 está documentada en el plan y en
  `workflow_orchestrator.py` pero NO fue leída en detalle en esta
  sesión. Re-validar en Tarea 0.J.
