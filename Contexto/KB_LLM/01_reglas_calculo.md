# 01 — Reglas de cálculo (qué conceptos, qué fórmulas, qué citas)

> Esta nota resume las fórmulas implementadas (o por implementar) por el
> motor de liquidación. **No es exhaustiva**: si el motor tiene un método
> que no figura aquí, gana el método (ver `00_fuente_de_verdad.md`).

## Convenciones globales

- **Base de días:** `params[*].DIAS_BASE = 360.0` (no 365). Esto es
  convención laboral colombiana para prestaciones, no error.
- **Base de vacaciones:** `VACACIONES_DENOM = 720.0` (= 360 × 2,
  denominador de la fracción cuando se pagan en dinero).
- **Redondeo:** controlado por `params[*].REDONDEO` (entero, decimales a
  conservar). Por defecto 0 (sin redondeo intermedio, ajustar al final).
- **Salario Base de Liquidación (SBL):** en `liquidator/calculators/sbl_calculator.py`
  se calcula como `salario_mensual + auxilio_transporte (si aplica) + promedio
  variable últimos 6 meses`. Auxilio de transporte aplica solo si
  `auxilio_transporte=true` y el contrato NO es de finca rural con
  residencia (ver regla V003, `params/checklist.json` y norma `CST_161`).
- **Tope de indemnización Art. 64 CST:** `params[*].TOPE_INDEMNIZACION_SMMLV = 20`
  (multiplicador sobre SMMLV, no implementado en v2.0 — ver riesgos).

## Concepto: Cesantías (CST 249-252)

- **Fórmula por segmento:**
  `cesantias = SBL × días_trabajados_segmento / 360`
- **Anualización:** si el periodo cruza 1 de enero, se segmenta por año
  calendario. Cada año usa el `params/<año>.json` que le corresponde y
  el **SBL del año** correspondiente (SL2630-2024: cada año calendario
  se liquida con el promedio del salario de ESE año). Implementado en
  `liquidator/core/salario_resolver.py` (Tarea 2.B-bis, S27).
  Ver sección \"Anualización salarial SL2630-2024\" abajo.
- **Plazo de pago:** 14 de febrero del año siguiente (ver
  `params/normas.json` → `plazos_pago.cesantías`, norma `CST_249_252`).
- **Implementación:** `liquidator/calculators/prestaciones_calculator.py`
  clase `PrestacionesCalculator`. Verificar que en el caso canónico
  (206 días, 2 segmentos) el motor sume correctamente 46/360 (segmento
  2025) + 160/360 (segmento 2026) sobre SBL = 2.200.000.

## Concepto: Intereses sobre cesantías (Ley 50/1990 Art. 99)

- **Fórmula:** `intereses = cesantias × 0.12 × (días_segmento / 360)`.
- **Tasa:** `TASA_INT_CESANTIAS = 0.12` anual. Codificada en
  `params/2025.json` y `params/2026.json` y referenciada en
  `params/normas.json` entrada `LEY50_99`.
- **Variante Ley 2466/2025 Art. 64:** pago mensual opcional del 1% del
  SBL (nominal anual = 12%) **solo si hay acuerdo escrito**. Codificada
  en `params/normas.json` entrada `LEY_2466_2025_INTERESES_MENSUALES`
  con `fecha_aplicacion = "2026-01-01"`. El motor **no** debe invocarla
  por defecto; debe detectar el flag `intereses_mensuales_acuerdo: true`
  en el input.
- **Plazo de pago anual:** 31 de enero del año siguiente
  (`plazos_pago.intereses_cesantias`).

## Concepto: Prima de servicios (CST 306-308)

- **Fórmula:** `prima = SBL × días_semestre / 360`.
- **Semestres:** H1 (1-ene a 30-jun, pago 30-jun) y H2 (1-jul a 31-dic,
  pago 20-dic). Si el contrato inicia/termina a mitad, se calcula
  proporcional.
- **Plazos:** `plazos_pago.prima_junio = 30/6`, `plazos_pago.prima_diciembre = 20/12`.

## Concepto: Vacaciones (CST 186-192)

- **Fórmula base (causación):** `vacaciones = (dias_servicio / 360) × 15`
  (15 días hábiles por año, Art. 186 CST).
- **Fórmula en dinero (acuerdo mutuo):** `vacaciones = (SBL × 15) / 720`
  (Art. 192 CST, denominador 720).
- **Fórmula compensación en finiquito (Art. 189-190):**
  `vacaciones_compensadas = (SBL / 30) × dias_pendientes`
  — **IMPLEMENTADO S29 (Tarea 2.B-ter)** en `PrestacionesCalculator.
  calculate_vacaciones_compensadas_finiquito`. Se invoca solo en modo
  FINIQUITO con `dias_pendientes > 0`. El SBL para vacaciones excluye
  recargos/HHE (Art. 185) y auxilio de transporte. Redondeo: ROUND_HALF_UP
  al peso. El renglón se inyecta en `desglose["vacaciones_compensadas_finiquito"]`.
- **Modo PERIODICA:** se pagan solo los días disfrutados o compensados
  voluntariamente. Acumulación pasiva al siguiente periodo. PERIODICA NO
  invoca `calculate_vacaciones_compensadas_finiquito` (regresión dura).
- **Modo FINIQUITO:** se pagan todas las vacaciones causadas y no
  disfrutadas, INCLUIDAS las fracciones. El motor distingue entre
  compensación por acuerdo mutuo (Art. 189, periodo vigente) y
  compensación obligatoria en finiquito (Art. 189 párr. 1° + Art. 190,
  terminación del contrato). El hook `_calcular_vacaciones_si_finiquito`
  en `engine.py` solo activa en modo FINIQUITO.
- **Verificación Art. 189 párr. 1° CST:** entrada `CST_189_VACACIONES`
  en `params/normas.json` — pendiente de verificación en SUIN
  (bloqueante para cerrar 2.B-ter).

## Concepto: Indemnización por despido sin justa causa (CST 64)

- **Estado v2.0:** **NO IMPLEMENTADO**. Ver reparo (c) addendum finiquito
  y entrada `06_riesgos_modelo.md` (riesgo R-LEG-01). El motor no debe
  emitir valores de indemnización en v2.0.0; queda referenciada en esta
  nota y en `params/normas.json` (`CST_64`) para casos futuros (Fase 4+).
- **Fórmula legal esperada (referencia):** 30 días primer año + 20 días
  cada año subsiguiente. Tope: `params[*].TOPE_INDEMNIZACION_SMMLV × SMMLV`
  = 20 × SMMLV del año de terminación.

## Concepto: Recargo dominical / festivo (Ley 2466/2025)

- **Cronograma gradual** (codificado en `params/normas.json` entrada
  `LEY_2466_2025`, campo `cronograma`):
  - 2024-07-01 → 2025-06-30: 0.75 (régimen anterior, Decreto 374/2024).
  - 2025-07-01 → 2026-06-30: 0.80 (primera fase Ley 2466/2025).
  - 2026-07-01 → 2027-06-30: 0.90 (segunda fase).
  - 2027-07-01 → ∞: 1.00 (tope pleno).
- **Implementación:** `liquidator/legal/recargos_manager.py` debe leer
  la fecha de pago/fecha_corte y aplicar el factor vigente.

## Lo que NO está cubierto en v2.0 (referencia a Fase 4+)

- **Liquidación detallada de horas extras** (CST 128): se referencia la
  norma, pero el motor no calcula recargo por hora extra individual; solo
  el promedio mensual si se incluye en `salario.variable`.
- **Aportes a seguridad social** (salud, pensión, ARL): fuera de alcance
  del liquidador de prestaciones.
- **Retención en la fuente**: tampoco; el output es bruto.
- **IPC / indexación de valores:** en planificación para Fase 2-bis
  (addendum SL2630-2024). Ver `02_parametros_vigentes.md` nota sobre
  IPC y `03_fuentes_normativas.md` sobre SL2630-2024.

## Anualización salarial SL2630-2024 (Tarea 2.B-bis, S27)

> **Fuente:** Addendum `addendum_sl2630_y_ipc_2026-06-09.md`, Sentencia
> SL2630-2024 Corte Suprema de Justicia, Sala de Descongestión Laboral
> N.º 1 (pendiente verificación verbatim).

**Principio:** cada año calendario se liquida con el promedio del
salario de ESE año. El SBL deja de ser un valor único del contrato.

**Resolución de SBL por año — 3 prioridades:**

1. **`historial_salarial`** — serie mensual (`list[MesValor]`).
   El motor calcula el promedio de los meses cuyo `año` coincide con
   el año del segmento.
2. **`sbl_por_anio`** — dict explícito `{año: SBL}`.
3. **`SBL` único** — compatibilidad con v1.x y caso canónico.

**Implementación:** `liquidator/core/salario_resolver.py` clase
`SalarioResolver` + dataclass `SegmentoCalculo` + helper
`segmentar_periodo()`. Integrado en `WorkflowOrchestrator`:
cuando el input contiene `sbl_por_anio` o `historial_salarial` en el
objeto `salario` (Pydantic `Salario` de 1.C-bis), el orquestador
activa la vía segmentada que calcula cesantías por año calendario
con el SBL resuelto para cada año.

**Tests:** 15 unitarios (`test_salario_resolver.py`) + 9 golden
(`test_salario_variable_por_anio.py`). Regresión canónica verde.

## Indexación por IPC (Tarea 2.X, S28 — Fase 2-bis, addendum SL2630-2024)

> **Fuente:** Addendum `addendum_sl2630_y_ipc_2026-06-09.md` (reparos
> bloqueantes b y c cerrados con `estado_verificacion: PENDIENTE_VERBATIM`
> en `params/normas.json`).
> **Marco legal:** SL2630-2024 (anualización + indexación) + **Art. 488
> CST** (prescripción 3 años desde fecha_exigibilidad).

**Principio:** las prestaciones adeudadas de años anteriores, no
pagadas oportunamente, deben **actualizarse a valor presente** usando
el IPC acumulado publicado por el DANE. La fórmula legal:

```
VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_origen)
```

donde `IPC_origen` se toma a la fecha de causación y `IPC_referencia`
a la fecha de pago efectivo (o la fecha de referencia solicitada).

**Activación (opt-in):** el input declara
`periodos_no_pagados: list[PeriodoNoPagado]`. Si el campo es `None`
o lista vacía, el motor se comporta como v2.0.0 (sin indexación).

**Validación de prescripción (Art. 488 CST):** si la diferencia entre
`fecha_referencia_indexacion` y `fecha_exigibilidad` supera 3 años,
el periodo se considera prescrito y se emite WARNING (no FAIL). El
renglón aparece en el desglose como `<concepto>_indexado_prescrito`
con `valor: 0` y `estado: "PRESCRITO"`.

**Defensa contra confusión índice/tasa (reparo c):** la clase
`IPCIndexador` (en `liquidator/calculators/indexacion.py`) rechaza
valores entre 0 y 1 en el constructor, lo que captura tasas anuales
disfrazadas de índices. Test:
`test_reparo_c_ipc_es_indice_no_tasa`.

**Fuente de datos:** `params/ipc_dane_mensual.json` (generado por
`scripts/build_ipc_index.py` a partir de la variación anual DANE
oficial). El script valida internamente que los cocientes
`dic/Y / dic/(Y-1)` reproducen exactamente la variación anual
declarada (tolerancia 0.1% para años 2+; 0.5% para el año base 2010
por la asimetría 11 vs 12 transiciones).

**Implementación:**
- `liquidator/calculators/indexacion.py` — clase `IPCIndexador`.
- `liquidator/contracts/input_model.py` — modelo `PeriodoNoPagado`
  (con `model_validator` de consistencia de fechas:
  `causacion <= exigibilidad <= referencia`).
- `liquidator/core/engine.py` — método `_procesar_periodos_no_pagados`
  integrado en `process_input()`. Carga la fuente, valida
  prescripción, calcula VA, inyecta renglones en `desglose` y suma
  al `total_liquidacion`.
- `liquidator/compliance/rule_evaluator.py` — regla `V011`
  (V_INDEXACION_IPC) con severidad MEDIUM, no bloqueante.
- `params/normas.json` — entradas `SL2630_2024` y `CST_488_PRESCRIPCION`
  (ambas `PENDIENTE_VERBATIM`).
- `params/checklist.json` — regla `V011` con `formula` y `nota`.

**Tests:**
- 24 unitarios (`test_indexacion.py`, 4 clases) — defensa en
  profundidad, casos ficticios del plan, integración con datos DANE
  reales, conformidad con reparos.
- 12 golden (`test_prescripcion_indexada.py`, 3 clases) — caso golden
  con periodo indexable, caso de prescripción, no-regresión del
  caso canónico.

**Limitación documentada:** la distribución mensual del índice es
**geométrica uniforme** (factor = `(1 + r_anual)^(1/12)`), lo cual
reproduce la variación anual DANE al cierre de cada año, pero **NO
preserva la estacionalidad intra-anual real** (los meses de enero
y diciembre suelen diferir del promedio). Para liquidaciones que
requieren precisión sub-anual, sustituir por la serie mensual DANE
oficial cuando se requiera (modificar `scripts/build_ipc_index.py`
para leer `ipc_mensual_dane.csv` con variación mensual directa).

**Reparos pendientes (no bloquean DoD de la tarea, sí bloquean v2.0
release):**
- Verificación verbatim de SL2630-2024 (texto literal, sala, URL
  oficial en relatoría/SIUGJ). R-LEG-03.
- Verificación verbatim de Art. 488 CST (texto literal en SUIN).

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S28, Tarea 2.X — Fase 2-bis).
