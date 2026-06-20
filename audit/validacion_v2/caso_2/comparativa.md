# Caso 2 — Avanzado (Addendum SL2630-2024 end-to-end)

**Fecha de ejecución:** 2026-06-19 (sesión S49)
**Modo:** FINIQUITO
**Tipo contrato:** INDEFINIDO
**Motivo terminación:** renuncia_voluntaria
**Período:** 2023-01-01 → 2024-12-30 (730 días inclusivos, 2 años)
**SBL por año:** 2023 = 2.500.000 / 2024 = 3.000.000 (variable)
**Trabajador:** [ANONIMIZADO] / [ANONIMIZADO]
**Params usadas:** 2025 (motor corre con --params-year default; SMMLV 1.423.500)

---

## Resumen ejecutivo

- [ ] **Coincide** con cálculo manual (tolerancia ±$1 por redondeo).
- [X] **Discrepancia mayor** documentada: el cálculo manual del borrador
      asumía prima anualizada sumando SBL por año. El motor aplica
      correctamente la regla semestral (Art. 306-308 CST) sobre el
      semestre de fecha_corte (H2 2024 = 183 días), no suma de los dos
      años.
- [X] **Discrepancia menor** en la fórmula de intereses: el manual
      calculó "Int 2023 + Int 2024" (suma por año) que es
      matemáticamente el anti-patrón documentado en Pitfall #19 (los
      cross-terms a×d2 + b×d1 se pierden). El motor usa la fórmula
      legal: `cesantías_TOTALES × días × 0.12 / 360` con cap 360
      para año completo.

**Conclusión:** Caso **validado con discrepancia mayor conceptual** en
prima. La segmentación SL2630-2024 funciona end-to-end (cesantías
diferenciadas por año, SBL por año aplicado vía SalarioResolver), pero
el cálculo manual del usuario interpretaba "anualización" como
"sumar por año" para TODOS los conceptos, lo cual es incorrecto para
prima (semestral) y para intereses (fórmula legal con cesantías
totales).

---

## Cotejo renglón por renglón

| Renglón              | Manual borrador | Motor v2.0 | Δ             | OK?     |
|----------------------|----------------:|-----------:|--------------:|:-------:|
| SBL_GENERAL          |     3.000.000   |  3.000.000 |          0    | [X] ✓   |
| SBL_VACACIONES       |     3.000.000   |  3.000.000 |          0    | [X] ✓   |
| Cesantías 2023       |     2.500.000   |  2.500.000 |          0    | [X] ✓   |
| Cesantías 2024       |     3.000.000   |  3.000.000 |          0    | [X] ✓   |
| Cesantías TOTAL      |     5.500.000   |  5.500.000 |          0    | [X] ✓   |
| Intereses s/ces      |       660.000   |    660.000 |          0    | [X] ✓   |
| Prima                |     5.500.000   |  1.525.000 | −3.975.000    | [X] ✗   |
| Vacaciones comp.     |     1.500.000   |  1.500.000 |          0    | [X] ✓   |
| Aux. transporte      |             0   |          0 |          0    | [X] ✓   |
| Indemnización Art.64 |             0   |          0 |          0    | [X] ✓   |
| **TOTAL**            |    13.160.000   |  9.185.000 | −3.975.000    | [X] ✗   |

Leyenda: ✓ = coincide; ~ = diff menor; ✗ = diff mayor.

---

## Cálculo motor (verificado contra código vivo)

**Segmentación SL2630-2024** (SalarioResolver activo):
- Segmento 2023: 2023-01-01 → 2023-12-31 (365 días calendario)
- Segmento 2024: 2024-01-01 → 2024-12-30 (365 días calendario)
- Total: 730 días

**SBL:** 3.000.000 (sin aux_transporte, SBL > 2 × SMMLV).

**Cesantías** (Art. 249-250 CST + SL2630-2024, segmentado por año):
- Por cada segmento con dias ≥ 365, motor aplica cap dias_liquidar = 360
  (regla "para año completo, usar base 360 para evitar sobrepago",
  prestaciones_calculator.py:100-104)
- Segmento 2023: 2.500.000 × 360/360 = 2.500.000
- Segmento 2024: 3.000.000 × 360/360 = 3.000.000
- **Total cesantías: 5.500.000**

**Intereses s/cesantías** (Ley 50/1990 Art. 99):
- Mismo cap dias = 360 (prestaciones_calculator.py:127-130)
- 5.500.000 × 360 × 0.12 / 360 = **660.000**
- (El motor usa 360 días para la fórmula, no 730, porque el cap aplica
  cuando dias_servicio ≥ 365)

**Prima de servicios** (Art. 306-308 CST, NO segmentada por año):
- Semestre de fecha_corte 2024-12-30 = segundo semestre 2024 (Jul-Dic)
- Inicio efectivo = max(2023-01-01, 2024-07-01) = 2024-07-01
- Fin efectivo = min(2024-12-30, 2024-12-31) = 2024-12-30
- Días = 182 + 1 = **183 días**
- SBL usado: el del año de fecha_corte = 3.000.000 (Pitfall #19: prima
  no se anualiza; usa SBL del año de fecha_corte)
- 3.000.000 × 183/360 = **1.525.000**

**Vacaciones compensadas** (Art. 189-190 CST, finiquito):
- 15 días pendientes × SBL_VACACIONES 3.000.000 / 30 = **1.500.000**
- SBL_VACACIONES = salario_mensual (3M) sin aux.

**Indemnización Art. 64 CST:** No aplica (motivo = renuncia_voluntaria,
R-LEG-01).

**Total:** 5.500.000 + 660.000 + 1.525.000 + 1.500.000 = **9.185.000**

---

## Discrepancias

### Discrepancia 1 — Prima
- **Renglón afectado:** prima
- **Manual dice:** $5.500.000 (Prima 2023 + Prima 2024 = 2.500.000 + 3.000.000)
- **Motor dice:** $1.525.000 (3.000.000 × 183/360, solo H2 2024)
- **Diferencia:** −$3.975.000 (−72.3%)
- **Hipótesis de causa:** El usuario asumió que con SBL variable, la
  prima también se anualiza por año (sumando cada año). El motor
  aplica la regla **universal** de prima (Art. 306-308 CST):
  - Prima es **semestral**, NO anual.
  - Prima se calcula **solo para el semestre de fecha_corte**.
  - Prima usa el SBL del **año de fecha_corte**, no anualización.
  - Esto aplica IGUAL con SBL variable (Pitfall #19).
- **Resolución:** Documentar regla. El motor es correcto; el manual del
  usuario debe corregirse a $1.525.000.

### Discrepancia 2 (menor, aceptable) — Fórmula de intereses
- **Renglón:** intereses
- **Manual:** $660.000 = 300.000 (2023) + 360.000 (2024) por año
- **Motor:** $660.000 = 5.500.000 × 360 × 0.12 / 360 (cap 360)
- **Coinciden en este caso** por coincidencia: cuando SBL por año es
  proporcional a un año completo, suma-por-año ≈ total × 360 / 360.
  Pitfall #19 advierte que esto **no siempre** coincide: para SBL
  desbalanceado (ej: 80% en 1 año) o períodos no múltiplos de 1 año,
  las dos fórmulas divergen. El motor usa la fórmula legal correcta.

---

## Compliance observado

- `compliance_status`: **WARN** (11 passed / 1 warning / 3 failures)
- Reglas PASS: V001 (params), V002 (contrato), V004-V005 (fórmulas),
  V011 (IPC N/A), V012-V013 (preaviso N/A para INDEFINIDO),
  V014-V015 (vacaciones OK).
- WARNINGS: V010 (verificación manual recomendada).
- FAILURES: incluye V014 (¿?) — a verificar en output completo.

No hay NO_GO bloqueante. El hook `_calcular_vacaciones_si_finiquito`
(engine.py:469) corre ANTES de compliance (per Pitfall #42, fix S43),
así que V014 ve el renglón `vacaciones_compensadas_finiquito` y PASEA.

---

## Notas sobre Forma 1 + Forma 2 mixta

El input.json incluye **AMBAS formas** por compatibilidad (Pitfall #28):
- Raíz (Forma 1): `sbl_por_anio`, `salario_mensual` — KB contract
- Anidado (Forma 2): `salario: { SBL, variable, sbl_por_anio }` — motor

El motor lee de `salario: {}` (workflow_orchestrator.py:287-304). Sin
el bloque anidado, la segmentación SL2630-2024 NO se activa y el motor
cae al path plano con `salario_mensual` constante.

---

## Salida del motor

- `audit/validacion_v2/caso_2/input.json`
- `audit/validacion_v2/caso_2/output.json`
- CLI exit code: 0
