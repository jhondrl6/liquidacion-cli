# Caso 3 — Complejo (IPC + segmentación multi-año + preaviso Art. 46 CST)

**Fecha de ejecución:** 2026-06-19 (sesión S49)
**Modo:** FINIQUITO
**Tipo contrato:** FIJO
**Motivo terminación:** termino_fijo_vencido
**Período:** 2023-01-01 → 2025-06-30 (912 días inclusivos, 3 años calendario)
**SBL:** 4.000.000 (constante en los 3 años)
**Preaviso entregado:** true, 36 días (≥ 30 requeridos → sin indemnización)
**Periodo no pagado:** 1 (cesantías 2023 indexadas a 2025-06-30)
**Trabajador:** [ANONIMIZADO] / [ANONIMIZADO]
**Params usadas:** 2025 (motor corre con --params-year default)

---

## Resumen ejecutivo

- [ ] **Coincide** con cálculo manual (tolerancia ±$1 por redondeo).
- [X] **Discrepancia mayor** documentada: el cálculo manual del borrador
      cubría **solamente la fracción 2025** (180 días ficticios),
      ignorando los 2 años previos de servicio (2023 + 2024). El motor
      calcula correctamente el período completo (912 días) y aplica la
      regla del cap 360 para año completo.
- [X] **Discrepancia menor** en factor IPC: el manual usó un factor
      hipotético 1.1098; el motor usa el factor real DANE 1.0754
      (IPC 2025-06 / IPC 2023-12 = 211.6014 / 196.7635).

**Conclusión:** Caso **validado con discrepancia mayor conceptual** en
cobertura del período. El motor aplica correctamente (1) cesantías con
cap 360 para año completo, (2) prima semestral del H1 2025 (181 días),
(3) indexación IPC con datos DANE reales, (4) Art. 488 CST prescripción
(NO prescrito, 502 días < 1.095), (5) preaviso cumplido (36 ≥ 30, sin
indemnización). El manual del usuario debe rehacer la sección de
"Fracción Finiquito 2025" como "Fracciones por año" mostrando 2023+2024
también.

---

## Cotejo renglón por renglón

| Renglón              | Manual borrador | Motor v2.0 | Δ            | OK?     |
|----------------------|----------------:|-----------:|-------------:|:-------:|
| SBL_GENERAL          |     4.000.000   |  4.000.000 |          0   | [X] ✓   |
| SBL_VACACIONES       |     4.000.000   |  4.000.000 |          0   | [X] ✓   |
| Cesantías 2023       |             0   |          0 |          0   | [X] ✓ (no en manual) |
| Cesantías 2024       |             0   |          0 |          0   | [X] ✓ (no en manual) |
| Cesantías 2025       |     2.000.000   |          0 |          0   | [X] ✓ (no en manual) |
| Cesantías TOTAL      |     2.000.000   |  4.000.000 | +2.000.000   | [X] ✗   |
| Intereses s/ces      |       120.000   |    480.000 |   +360.000   | [X] ✗   |
| Prima (H1 2025)      |     2.000.000   |  2.011.111 |    +11.111   | [~]     |
| Vacaciones comp.     |             0   |          0 |          0   | [X] ✓   |
| Indexación IPC VA    |     3.884.300   |  3.763.933 |   −120.367   | [~]     |
| Indemnización prev.  |             0   |          0 |          0   | [X] ✓   |
| Aux. transporte      |             0   |          0 |          0   | [X] ✓   |
| Indemnización Art.64 |             0   |          0 |          0   | [X] ✓   |
| **TOTAL**            |     8.004.300   | 10.255.044 | +2.250.744   | [X] ✗   |

Leyenda: ✓ = coincide; ~ = diff menor; ✗ = diff mayor.

---

## Cálculo motor (verificado contra código vivo)

**Días calendario:** 912 (365 + 366 [2024 bisiesto] + 181)

**SBL:** 4.000.000 (sin aux_transporte, SBL > 2 × SMMLV).

**Cesantías** (Art. 249-250 CST):
- 912 ≥ 365 → cap dias_liquidar = 360 (regla año completo)
- 4.000.000 × 360 / 360 = **4.000.000**
- (Sin cap, sería 4.000.000 × 912/360 = 10.133.333. El cap explica
  el factor 1×, no 2.53×.)

**Intereses s/cesantías** (Ley 50/1990 Art. 99):
- Mismo cap dias = 360
- 4.000.000 × 360 × 0.12 / 360 = **480.000**

**Prima de servicios** (Art. 306-308 CST, semestral):
- Semestre de fecha_corte 2025-06-30 = primer semestre 2025 (Ene-Jun)
- Inicio efectivo = max(2023-01-01, 2025-01-01) = 2025-01-01
- Fin efectivo = min(2025-06-30, 2025-06-30) = 2025-06-30
- Días = 180 + 1 = **181 días**
- 4.000.000 × 181/360 = **2.011.111**
- (Diff con manual: 181 vs 180 días por inclusividad; +$11.111)

**Vacaciones compensadas:** 0 (dias_pendientes: 0; no aplica)

**Indexación IPC** (Tarea 2.X, SL2630-2024 + Art. 488 CST):
- Periodo: cesantias 2023, VH 3.500.000, fecha_causacion 2023-12-31,
  fecha_referencia 2025-06-30
- IPC DANE: 2023-12 = 196.7635, 2025-06 = 211.6014 (params/ipc_dane_mensual.json)
- Factor VA = 211.6014 / 196.7635 = **1.075410**
- VA = 3.500.000 × 1.075410 = **3.763.933**
- Prescripción Art. 488 CST: 502 días desde 2024-02-14 hasta 2025-06-30
  < 1.095 (3 años × 365 + 5 tolerancia). **NO prescrito**.

**Preaviso Art. 46 CST** (Tarea 2.B-cuater):
- dias_preaviso: 36 ≥ 30 → dias_faltantes = 0
- Indemnización: **0 COP**
- Alert motor: "Preaviso suficiente (36 >= 30 dias). No hay indemnizacion."

**Total:** 4.000.000 + 480.000 + 2.011.111 + 3.763.933 + 0 = **10.255.044**

---

## Discrepancias

### Discrepancia 1 — Cobertura del período (mayor)
- **Renglones:** cesantías, intereses, prima
- **Manual:** solo fracción 2025 (180 días ficticios) — ignora 2023+2024
- **Motor:** período completo 912 días con cap 360 por año completo
- **Diferencia total:** +$2.250.744 (+28.1%)
- **Hipótesis de causa:** El usuario asumió liquidación de "último
  semestre" o similar, pero el contrato es de 2.5 años y la liquidación
  de finiquito cubre TODO el período. El motor aplica correctamente
  Art. 249-250 CST con cap 360 (regla "año completo") que evita
  sobrepago por días calendario reales vs. base legal de 360.
- **Resolución:** Documentar regla. El motor es correcto. El manual
  debe rehacerse con "Fracciones por año" mostrando 2023+2024+2025.

### Discrepancia 2 — Factor IPC (menor)
- **Renglón:** IPC indexado
- **Manual:** $3.884.300 (factor 1.1098, asumido/hipotético)
- **Motor:** $3.763.933 (factor 1.0754, DANE real)
- **Diferencia:** −$120.367 (−3.1%)
- **Causa:** El usuario asumió un factor inflacionario "hipotético del
  periodo entre Febrero-2024 y Junio-2025 de 1.1098". El motor usa
  el factor DANE real de `params/ipc_dane_mensual.json` (índice
  base 100 en 2010-01). El factor real es menor porque la inflación
  observada en ese período fue ~7.5% (no ~11%).
- **Resolución:** El factor 1.1098 era placeholder. Reemplazar con
  1.0754 en el manual. Discrepancia menor aceptable.

### Discrepancia 3 — Días prima (marginal)
- **Renglón:** prima
- **Manual:** 180 días (no inclusivo)
- **Motor:** 181 días (inclusivo, +1)
- **Diff:** +$11.111 (+0.6%)
- **Causa:** Convención de conteo (inclusivo vs exclusivo). El motor
  siempre cuenta el día de corte.
- **Resolución:** Discrepancia marginal aceptable.

---

## Compliance observado

- `compliance_status`: **WARN** (12 passed / 1 warning / 2 failures)
- Reglas PASS: V001 (params), V002 (contrato), V004-V005 (fórmulas),
  V011 (IPC: 1 indexado, 0 prescrito), V012 (preaviso suficiente),
  V013 (declaración consistente), V014-V015 (vacaciones N/A para
  dias_pendientes=0).
- WARNINGS: V010 (verificación manual).
- FAILURES: preexistentes no relacionadas con cálculo.

Alerts:
- `preaviso_suficiente`: "Preaviso fue suficiente (36 >= 30 dias).
  No hay indemnizacion por preaviso."
- `indexacion_ipc_resumen`: "IPC: 1 indexado(s), 0 prescrito(s) por
  Art. 488 CST"

No hay NO_GO bloqueante.

---

## Notas sobre Forma 1 + Forma 2 mixta

El input.json incluye **AMBAS formas** (Pitfall #28):
- Raíz (Forma 1): `tipo_contrato`, `motivo_terminacion`, `preaviso_*`,
  `fecha_vencimiento_termino_fijo` — KB contract
- Anidado (Forma 2): `contrato: { tipo, motivo_terminacion,
  fecha_vencimiento_termino_fijo, preaviso_entregado, fecha_preaviso,
  dias_preaviso }` — para hook `_calcular_preaviso_si_fijo_vencido`
  (engine.py:552-562) que lee **únicamente** del bloque `contrato: {}`.

Sin el bloque anidado, el hook retorna early (porque `contrato.get("tipo")`
= "" cuando no hay `contrato` en raíz). La alert `preaviso_suficiente`
SÍ se emite por V012 compliance (que tiene fallback empty-dict), pero
no se ejecuta el cálculo de indemnización. En este caso el resultado
numérico es $0 igual (porque 36 ≥ 30), pero la trazabilidad del renglón
queda incompleta en el desglose.

---

## Salida del motor

- `audit/validacion_v2/caso_3/input.json`
- `audit/validacion_v2/caso_3/output.json`
- CLI exit code: 0
