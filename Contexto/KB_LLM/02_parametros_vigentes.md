# 02 — Parámetros vigentes (SMMLV, aux_trans, tasas, plazos por año)

> **REGLA DURA:** nunca hardcodear SMMLV, auxilio de transporte, límites
> ni tasas. Todo valor numérico de liquidación debe provenir de
> `params/<año>.json` del año correspondiente al segmento.

> **Tarea 0.K cerrada en S11 (2026-06-13).** Este archivo fue
> renombrado de `02_parametros_2025.md` (legado, Tarea 0.E) a
> `02_parametros_vigentes.md`. La tabla comparativa 2025 vs 2026
> es la fuente de verdad operativa para el motor year-aware
> (Tarea 1.E de Fase 1). Los params/2025.json y params/2026.json
> en `params/` son los datos crudos; esta nota es la lectura
> humana + regla de selección por `fecha_corte`.

---

## Tabla comparativa 2025 vs 2026 (vigentes al 2026-06-13)

| Concepto                          | 2025                          | 2026                          | Fuente normativa                          | Estado verificación      |
|-----------------------------------|-------------------------------|-------------------------------|-------------------------------------------|--------------------------|
| **SMMLV**                         | $1.423.500                    | $1.750.905                    | D. 1572/2024 (2025) · D. 1469/2025 / D. 159/2026 (2026) | 2025 ✓ / 2026 ✓ valor, ⚠ acto transitorio |
| **Auxilio de transporte**         | $200.000                      | $249.095                      | D. 1573/2024 (2025) · D. 1470/2025 (2026) | 2025 ✓ / 2026 ✓         |
| **Límite aux_trans (2×SMMLV)**    | $2.847.000                    | $3.501.810                    | Derivado (2×SMMLV del año)                | ✓ regla permanente       |
| **Tasa int. cesantías**           | 0.12 anual (12%)              | 0.12 anual (12%)              | Ley 50/1990 Art. 99                       | ✓ permanente             |
| **Variante pago mensual int. ces.**| NO                            | Teóricamente opcional (Art. ? Ley 2466/2025) | Ley 2466/2025 — **R-LEG-NUEVO-01 PENDIENTE** | ⚠ cita legal sin verificar verbatim |
| **DIAS_BASE**                     | 360                           | 360                           | D. 1072/2015                              | ✓ permanente             |
| **VACACIONES_DENOM**              | 720                           | 720                           | CST Arts. 186-192                         | ✓ permanente             |
| **Recargo dominical vigente**     | 0.80 (desde 2025-07-01)       | 0.80 hasta 2026-06-30, 0.90 desde 2026-07-01 | Ley 2466/2025 Arts. 13-14 (cronograma gradual 0.75→0.80→0.90→1.00) | ✓ cronograma en normas.json |
| **Tope indem. (SMMLV)**           | 20                            | 20                            | CST Art. 64                               | ✓ permanente             |

> **Nota crítica 2026:** el SMMLV $1.750.905 **está vigente** pero el acto
> administrativo que lo fijó cambió. El Decreto 1469/2025 fue suspendido
> provisionalmente por el Consejo de Estado (Auto del 2026-02-12, Exp.
> 11001-03-25-000-2026-00004-00) y re-fijado por el Decreto 159/2026 del
> 2026-02-19 con el **mismo valor** ($1.750.905). El motor usa el valor;
> la metadata cita **ambos decretos** para trazabilidad. La suspensión
> es **provisional** y está pendiente de sentencia de nulidad.

---

## Fuente normativa de cada año

### 2025
- **SMMLV:** Decreto 1572/2024 → 1.423.500. Ver `params/normas.json`
  entrada `DECRETO_1572_2024` (url SUIN, valor, vigencia "2025").
- **Auxilio de transporte:** Decreto 1573/2024 → 200.000. Ver
  `params/normas.json` entrada `DECRETO_1573_2024`.
- **Límite (2×SMMLV):** derivado, no decreto separado. Si SBL ≤ 2.847.000
  → aplica aux_trans; si > 2.847.000 → NO aplica (regla V003,
  `params/checklist.json`).
- **Tasa intereses cesantías:** Ley 50/1990 Art. 99 → 0.12 anual.
  Permanente, no cambia por año. Ver `params/normas.json` entrada
  `LEY50_99`.
- **Recargo dominical:** 0.80 desde 2025-07-01 (Ley 2466/2025 Art. 14).

### 2026
- **SMMLV:** $1.750.905. **Dos actos administrativos vigentes:**
  - **Decreto 1469/2025** (30-dic-2025) — suspendido provisionalmente por
    Consejo de Estado desde 2026-02-12. Ver `params/normas.json`
    entrada `DECRETO_1469_2025` (`estado_verificacion:
    SUSPENDIDO_PROVISIONALMENTE`, URL SUIN real verificada).
  - **Decreto 159/2026** (19-feb-2026) — re-fijación transitoria con
    **mismo valor** $1.750.905, vigente hasta sentencia de nulidad. Ver
    `params/normas.json` entrada `DECRETO_159_2026`
    (`estado_verificacion: VERIFICADO`).
  - **Recomendación al motor:** usar el valor; registrar en output
    `meta.referencias_normativas` ambos decretos. Si la nulidad prospera,
    el SMMLV 2026 volverá a 1.423.500 (con retroactivo); re-validar antes
    de v2.0 release.
- **Auxilio de transporte:** Decreto 1470/2025 → 249.095. Vigente
  desde 2026-01-01. Ver `params/normas.json` entrada
  `DECRETO_1470_2025`. URL SUIN real verificada 2026-06-13.
- **Límite (2×SMMLV):** 3.501.810 (derivado).
- **Tasa intereses cesantías:** sigue 0.12 anual (Ley 50/1990 NO se
  modificó).
- **Recargo dominical:** **0.80** vigente hasta 2026-06-30;
  **0.90** desde 2026-07-01 hasta 2027-06-30. Cronograma completo
  en `params/normas.json` entrada `LEY_2466_2025` (4 fases:
  0.75 / 0.80 / 0.90 / 1.00).
- **Variante pago mensual intereses sobre cesantías (PENDIENTE):**
  el plan v2.0 (líneas 552-559) afirma que el "Art. 64 de la Ley
  2466/2025" permite pago mensual opcional del 1% del SBL (nominal
  anual = 12%) **solo si hay acuerdo escrito**. **Verificación
  SUIN del 2026-06-13** muestra que el Art. 64 de la Ley 2466/2025
  es **"Régimen simple laboral"**, NO pago mensual de intereses.
  **Issue R-LEG-NUEVO-01 (PENDIENTE_TEXTO_LITERAL):** la atribución
  del plan probablemente es incorrecta. El motor **NO debe aplicar**
  pago mensual de intereses sobre cesantías hasta verificar el
  artículo literal exacto. Entrada dejada en `params/normas.json`
  como `estado_verificacion: PENDIENTE_TEXTO_LITERAL` con URL
  general de la Ley 2466/2025.

---

## Regla de selección por `fecha_corte` (segmentación year-aware)

Cuando un contrato cruza 1 de enero (caso canónico: 2025-11-16 →
2026-06-09, 206 días en 2 segmentos), el motor **debe** segmentar por
año calendario y aplicar `params/<año>.json` a cada segmento.

**Pseudocódigo (a implementar en Tarea 1.E ParamsProvider de Fase 1):**

```
para cada segmento en [inicio, fin]:
    año = segmento.inicio.year
    si segmento cruza 1-ene:
        partir en [inicio, 31-dic] y [1-ene, fin]
        asignar params/2025.json al primero
        asignar params/2026.json al segundo
    sino:
        asignar params/<año>.json

# Caso 2025-11-16 → 2026-06-09:
#   Segmento A: 2025-11-16 → 2025-12-31 (45 días, params 2025)
#   Segmento B: 2026-01-01 → 2026-06-09 (160 días, params 2026)
#   Cesantías = (SBL/360) * 45  +  (SBL_2026/360) * 160
#   Intereses = 12% sobre cesantías de cada año calendario
```

**Auditoría:** el output debe registrar `meta.parametros_por_segmento`
con un objeto por segmento (no un único `params_version`). Ver plan §3
y `05_schema_salida.md`.

**Caso 2026-02-19 (suspensión del D. 1469/2025):** el SMMLV NO cambia
de valor en esa fecha (Decreto 159/2026 mantiene los $1.750.905). El
motor **no debe** detectar la suspensión como cambio de params; solo
debe registrarla en `meta.referencias_normativas` para trazabilidad
legal. Si en el futuro la nulidad reduce el SMMLV, se reabre Fase 1.

---

## URLs verificadas (SUIN + Alcaldía de Bogotá) — fuente normativa de Tarea 0.K

Las siguientes URLs fueron extraídas de SUIN-Juriscol (fuente oficial
primaria) y verificadas el **2026-06-13** durante Tarea 0.K. Cada
entrada de `params/normas.json` apunta a su URL verificada.

| Norma                       | URL SUIN (primaria)                                       | URL Alcaldía Bogotá (respaldo)                                       |
|-----------------------------|-----------------------------------------------------------|----------------------------------------------------------------------|
| Ley 2466/2025               | https://www.suin-juriscol.gov.co/viewDocument.asp?id=30055086 | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=181933&dt=S |
| Decreto 1469/2025 (SMMLV)   | https://www.suin-juriscol.gov.co/viewDocument.asp?id=30055940 | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=191925&dt=S |
| Decreto 1470/2025 (aux)     | https://www.suin-juriscol.gov.co/viewDocument.asp?id=30055941 | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=191926&dt=S |
| Decreto 159/2026 (trans.)   | (no en SUIN al 2026-06-13)                                | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=192181&dt=S |

URLs pendientes de verificar (placeholders históricos eliminados en S11):
ninguna para 2025/2026. Las 4 normas vigentes tienen URL real.

---

## Lo que falta para llegar a 2027+

- `params/2027.json` no existe aún. Se crea cuando se publique el
  decreto de SMMLV 2027 (esperado dic-2026/ene-2027).
- `scripts/check_kb_freshness.py` (Tarea 0.H, cerrado en S8) ya es
  year-aware: itera sobre todos los `params/<año>.json` presentes en
  `params/` y compara contra esta KB. Agregar `2027.json` no requiere
  tocar el script.
- `liquidator/tests/test_kb_freshness.py` (S8) ya está parametrizado
  para 2025/2026 — agregar 2027 a la lista parametrizada es trivial.

---

## IPC y valores históricos (Fase 2-bis, NO vigente aún)

El addendum SL2630-2024 (ver `Planificación/addendum_sl2630_y_ipc_2026-06-09.md`)
plantea indexar valores de prestaciones prescritas con IPC. El IPC debe
modelarse como **índices acumulados** del DANE, NO como tasas anuales
de inflación. La `IPCIndexador` aún no está implementada; cuando se
haga, los datos fuente deben ir a `data/ipc_dane/<año>.json` y la
regla `V_INDEXACION_IPC` al `params/checklist.json` con `severity: MEDIUM`
(no bloqueante).

---

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S11, Tarea 0.K).
- **Verificado:**
  - Lectura de `params/2025.json` y `params/2026.json` (12 y 13 líneas,
    valores coinciden con la tabla).
  - `params/normas.json` tiene 18 entradas: 4 con URL SUIN real
    verificada 2026-06-13 (Ley 2466/2025, Decretos 1469/2025, 1470/2025,
    159/2026), 12 con URLs de la doctrina CST/D. 1072, 1 con
    `estado_verificacion: PENDIENTE_TEXTO_LITERAL` (R-LEG-NUEVO-01).
  - Decreto 1469/2025 marcado `SUSPENDIDO_PROVISIONALMENTE` con
    `nota_estado` y Decreto 159/2026 registrado como acto vigente
    transitorio.
  - `scripts/check_kb_freshness.py` year-aware (S8): itera
    `params/<YYYY>.json` con glob `[0-9][0-9][0-9][0-9].json`.
  - `liquidator/tests/test_kb_freshness.py` (S8): parametrizado para
    2025 y 2026.
- **NO verificado (bloqueado por sistema en S11):** ejecución real de
  los 4 comandos de validación del plan §5.2 T0.K (el sistema denegó
  invocaciones a `python3` por seguridad perimetral; la ejecución
  quedó pendiente para próxima sesión con `python3`/`uv run`).
- **Riesgos legales nuevos (S11):**
  - **R-LEG-NUEVO-01** (PENDIENTE): atribución del plan v2.0 al
    "Art. 64 Ley 2466/2025" para pago mensual de intereses sobre
    cesantías contradice verificación SUIN. **NO implementar** en
    motor hasta verificar el artículo literal exacto.
  - **R-LEG-NUEVO-02** (VIGILAR): nulidad del Decreto 1469/2025
    podría revivir SMMLV 2025 = 1.423.500 con efecto retroactivo.
    Re-validar antes de v2.0 release.
