# 02 — Parámetros vigentes (SMMLV, aux_trans, tasas por año)

> **REGLA DURA:** nunca hardcodear SMMLV, auxilio de transporte, límites
> ni tasas. Todo valor numérico de liquidación debe provenir de
> `params/<año>.json` del año correspondiente al segmento.

## Vigentes al cierre de la sesión S5 (2026-06-13)

| Año | Archivo | SMMLV     | Aux. Trans. | Límite aux_trans (2×SMMLV) | Tasa int. ces. | DIAS_BASE | VAC_DENOM | Recargo dom. desde | Tope indem. (SMMLV) | Versión |
|-----|---------|-----------|-------------|----------------------------|----------------|-----------|-----------|--------------------|----------------------|---------|
| 2025 | `params/2025.json` | 1.423.500 | 200.000     | 2.847.000                  | 0.12 (12%)     | 360.0     | 720.0     | 2025-07-01 (factor 0.80) | 20        | 2025-10-31 |
| 2026 | `params/2026.json` | 1.750.905 | 249.095     | 3.501.810                  | 0.12 (12%)     | 360.0     | 720.0     | 2026-07-01 (factor 0.90) | 20        | 2026-06-09 |

> **Nota:** `params/2026.json` trae `FECHA_APLICACION_RECARGO_DOMINICAL = "2026-07-01"`,
> que es la fecha de cambio de fase **siguiente**, no la fecha actual.
> La fase vigente al 2026-06-09 es la **primera** (0.80), vigente
> desde 2025-07-01. Ver cronograma completo en `params/normas.json`
> entrada `LEY_2466_2025` (4 fases: 0.75 / 0.80 / 0.90 / 1.00).

## Fuente normativa de cada año

### 2025
- **SMMLV:** Decreto 1572/2024 → 1.423.500. Ver `params/normas.json`
  entrada `DECRETO_1572_2024` (url, valor, vigencia "2025").
- **Auxilio de transporte:** Decreto 1573/2024 → 200.000. Ver
  `params/normas.json` entrada `DECRETO_1573_2024`.
- **Límite (2×SMMLV):** derivado, no decreto separado. Si SBL ≤ 2.847.000
  → aplica aux_trans; si > 2.847.000 → NO aplica (regla V003,
  `params/checklist.json`).
- **Tasa intereses cesantías:** Ley 50/1990 Art. 99 → 0.12 anual.
  Permanente, no cambia por año. Ver `params/normas.json` entrada
  `LEY50_99`.

### 2026
- **SMMLV:** Decreto 1469/2025 → 1.750.905. Vigente desde 2026-01-01.
  Ver `params/normas.json` entrada `DECRETO_1469_2025`. **PENDIENTE:**
  la URL está como `?i=XXXXXX` (placeholder); antes de v2.0 release se
  debe verificar la URL real en SUIN y reemplazar.
- **Auxilio de transporte:** Decreto 1470/2025 → 249.095. Vigente
  desde 2026-01-01. Ver `params/normas.json` entrada
  `DECRETO_1470_2025`. **PENDIENTE:** misma observación sobre URL.
- **Límite (2×SMMLV):** 3.501.810 (derivado).
- **Tasa intereses cesantías:** sigue 0.12 anual (Ley 50/1990 NO se
  modificó).
- **Variante Ley 2466/2025 Art. 64:** pago mensual opcional del 1% del
  SBL (nominal anual = 12%) **solo si hay acuerdo escrito**.
  Codificado en `params/normas.json` entrada
  `LEY_2466_2025_INTERESES_MENSUALES` con `fecha_aplicacion = "2026-01-01"`.
  El motor no debe aplicarlo por defecto — solo si el input trae
  `intereses_mensuales_acuerdo: true`.

## Regla de selección por `fecha_corte` (segmentación)

Cuando un contrato cruza 1 de enero (caso canónico: 2025-11-16 →
2026-06-09), el motor **debe** segmentar por año calendario y aplicar
`params/<año>.json` a cada segmento. Pseudocódigo:

```
para cada segmento en [inicio, fin]:
    año = segmento.inicio.year
    si segmento cruza 1-ene:
        partir en [inicio, 31-dic] y [1-ene, fin]
        asignar params/2025.json al primero
        asignar params/2026.json al segundo
    sino:
        asignar params/<año>.json
```

Auditoría: el output debe registrar `meta.parametros_por_segmento` con
un objeto por segmento (no un único `params_version`). Ver plan §3
y `05_schema_salida.md`.

## Lo que falta para llegar a 2027+

- `params/2027.json` no existe aún. Se crea cuando se publique el
  decreto de SMMLV 2027 (esperado dic-2026/ene-2027).
- `scripts/check_kb_freshness.py` (Tarea 0.H) debe iterar sobre todos
  los `params/<año>.json` presentes en `params/` y comparar contra
  `KB_LLM/02_parametros_vigentes.md`. Hoy el script está esbozado en
  el plan §5.2 Tarea 0.H (líneas 408-498) pero no creado en disco.

## IPC y valores históricos (Fase 2-bis, NO vigente aún)

El addendum SL2630-2024 (ver `Planificación/addendum_sl2630_y_ipc_2026-06-09.md`)
plantea indexar valores de prestaciones prescritas con IPC. El IPC debe
modelarse como **índices acumulados** del DANE, NO como tasas anuales
de inflación. La `IPCIndexador` aún no está implementada; cuando se
haga, los datos fuente deben ir a `data/ipc_dane/<año>.json` y la
regla `V_INDEXACION_IPC` al `params/checklist.json` con `severity: MEDIUM`
(no bloqueante).

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** lectura de `params/2025.json` y `params/2026.json`
  (12 y 13 líneas respectivamente, valores coinciden con la tabla).
  `params/normas.json` revisado para los `id` citados.
- **NO verificado:** URLs reales de Decretos 1469/2025 y 1470/2025
  (siguen con `?i=XXXXXX`). Re-validar antes de v2.0 release.
