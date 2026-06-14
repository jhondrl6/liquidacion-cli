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

## Campos pendientes para Fase 1 (addendas)

- **Addendum finiquito (Tarea 1.C-ter):** añadir a `contrato`:
  - `motivo_terminacion` (enum `MotivoTerminacion` con 10 valores: `RENUNCIA_VOLUNTARIA`,
    `DESPIDO_SIN_JUSTA_CAUSA`, `DESPIDO_CON_JUSTA_CAUSA`, `TERMINO_FIJO_VENCIDO`,
    `OBRA_O_LABOR_TERMINADA`, `MUTUO_ACUERDO`, `MUERTE_TRABAJADOR`,
    `MUERTE_EMPLEADOR`, `SUSPENSION_DEFICITARIA`, `CIERRE_EMPRESA`).
    **IMPLEMENTADO S24 (1.C-ter).**
  - `VacacionesEstado` (sub-modelo con `dias_causados_proporcionales: Decimal | None`,
    `dias_disfrutados: Decimal = 0`, `dias_pendientes: Decimal (ge=0)`,
    `fechas_disfrute: list[PeriodoDisfrute] | None`). Con `model_validator`
    que rechaza `dias_pendientes > dias_causados - dias_disfrutados`.
    **IMPLEMENTADO S24 (1.C-ter).**
  - `Contrato.fecha_terminacion_real: date | None` agregado.
  - `model_validator` en `Contrato`: fecha_terminacion_real requiere motivo.
  - `model_validator` en `LiquidacionInput`: FINIQUITO requiere motivo_terminacion.
- **Addendum SL2630 (Tarea 1.C-bis):** añadir a `salario` (IMPLEMENTADO en
  S23, retrocompatible):
  - `sbl_por_anio` (dict `{anio: monto}`) para contratos multi-año
    con SBL variable. Por defecto el SBL es único (caso canónico), pero
    el motor debe aceptar la estructura anualizada.
  - `historial_salarial` (list de `MesValor` con `año`/`mes`/`valor`)
    para salario variable real (promedio del año del segmento).
  - `model_validator` rechaza `variable=True` sin
    `sbl_por_anio` ni `historial_salarial`.

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

- **Fecha:** 2026-06-13 (sesión S24, Tarea 1.C-ter).
- **Verificado:** `liquidator/contracts/input_model.py` con `MotivoTerminacion`
  (10 valores), `PeriodoDisfrute`, `VacacionesEstado`, `Contrato` actualizado
  (`motivo_terminacion: MotivoTerminacion | None`, `fecha_terminacion_real`,
  `model_validator` `_terminacion_real_requiere_motivo`), `LiquidacionInput`
  actualizado (`vacaciones: VacacionesEstado | None`,
  `model_validator` `_finiquito_requiere_motivo`).
- **Tests:** 69/69 PASS en `test_contracts/` (17 input + 12 output + 10 salario
  extendido + 15 vacaciones + 15 motivo terminación). 11/11 PASS en caso
  canónico (regresión cero).

## Schema Pydantic formal (S16 — Tarea 1.C, plan §6.2)

A partir de la sesión S16 (2026-06-13, commit `6a58f08`), el contrato
de entrada tiene modelo Pydantic v2 en
`liquidator/contracts/input_model.py`:

- `LiquidacionInput` (top-level)
- `Trabajador` (sub-modelo: `nombre`, `documento`)
- `Empleador` (sub-modelo: `nombre`, `documento`)
- `Contrato` (sub-modelo: `fecha_ingreso`, `fecha_corte`, `tipo`,
  `motivo_terminacion: MotivoTerminacion | None = None`,
  `fecha_terminacion_real: date | None = None`. **Extensión 1.C-ter S24**:
  `model_validator` rechaza `fecha_terminacion_real` sin motivo.)
- `Salario` (sub-modelo: `SBL: Decimal` con `Field(gt=0)`,
  `auxilio_transporte: bool = False`, `variable: bool = False`,
  `dias_trabajados: int | None = None`)
- `VacacionesEstado` (sub-modelo: `dias_causados_proporcionales: Decimal | None = None`,
  `dias_disfrutados: Decimal = Decimal(0)`,
  `dias_pendientes: Decimal = Field(ge=0)`,
  `fechas_disfrute: list[PeriodoDisfrute] | None = None`.
  **Extensión 1.C-ter S24**: tipado, reemplaza `vacaciones: dict | None`.)
- `MotivoTerminacion` (enum con 10 valores Arts. 45-49 CST. **1.C-ter S24**)
- `PeriodoDisfrute` (sub-modelo con `desde: date`, `hasta: date`. **1.C-ter S24**)

Validaciones implementadas en la base 1.C:

- `field_validator("contrato")` garantiza `fecha_corte >= fecha_ingreso`
  (lanza `ValueError` claro si se invierte).
- `modo` es `Literal["PERIODICA", "FINIQUITO", "VACACIONES"]`.
- `contrato.tipo` es `Literal["INDEFINIDO", "FIJO", "OBRA_LABOR",
  "PRESTACION"]` (MAYÚSCULAS obligatorias).
- `SBL` se valida con `Field(gt=0)` — rechaza 0 y negativos.
- Forma 1 (plana) NO es rechazada por el schema (porque NO es entrada
  del schema formal); sigue entrando vía `InputParser` legacy hasta
  Tarea 1.D.

Extensiones planificadas (no en 1.C base, son tareas separadas
anidadas en Fase 1):

- **1.C-bis** (addendum SL2630-2024, **IMPLEMENTADO S23**): `Salario.sbl_por_anio:
  dict[int, Decimal] | None`, `Salario.historial_salarial:
  list[MesValor] | None`, sub-modelo `MesValor` con `año: int`,
  `mes: int` (1-12), `valor: Decimal` (>0), `model_validator` rechaza
  `variable=True` sin historial. Ver `liquidator/contracts/input_model.py`.
- **1.C-ter** (addendum finiquito/vacaciones, **IMPLEMENTADO S24**):
  `Contrato.motivo_terminacion: MotivoTerminacion` (enum Arts. 45-49
  CST), `VacacionesEstado` tipado (reemplaza `vacaciones: dict`),
  `Contrato.fecha_terminacion_real: date | None`. Ver
  `liquidator/contracts/input_model.py`.
- **1.C-quater** (addendum preaviso, **IMPLEMENTADO S25**):
  `Contrato.preaviso_entregado: bool | None`,
  `Contrato.fecha_preaviso: date | None`,
  `Contrato.dias_preaviso: int | None`,
  `Contrato.fecha_vencimiento_termino_fijo: date | None` +
  `_preaviso_consistencia` (regla 1: solo aplica a FIJO;
  regla 2: `preaviso_entregado=True` exige `fecha_preaviso`;
  regla 3: FINIQUITO+FIJO+vencido exige `preaviso_entregado` declarado).
  Preaviso aplica exclusivamente a contrato a término fijo (Art. 46 CST).
  El motor consume estos campos en Tarea 2.B-cuater (Fase 2) para
  calcular la indemnización por preaviso insuficiente. Ver
  `liquidator/contracts/input_model.py` y
  `liquidator/tests/test_contracts/test_preaviso_contrato.py` (16 tests).

**Validación contra tests:** 17/17 PASS en
`liquidator/tests/test_contracts/test_input_model.py` (S16) + 10/10 PASS
en `liquidator/tests/test_contracts/test_salario_extendido.py` (S23,
extensión 1.C-bis) + 15/15 PASS en `test_vacaciones_estado.py` (S24,
extensión 1.C-ter) + 15/15 PASS en `test_motivo_terminacion.py` (S24,
extensión 1.C-ter) + **16/16 PASS en `test_preaviso_contrato.py` (S25,
extensión 1.C-quater)**. Total `test_contracts/`: **85/85 PASS**.
