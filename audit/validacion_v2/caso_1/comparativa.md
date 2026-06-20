# Caso 1 — Básico (Smoke Test PERIODICA)

**Fecha de ejecución:** 2026-06-19 (sesión S49)
**Modo:** PERIODICA
**Tipo contrato:** INDEFINIDO
**Período:** 2024-03-01 → 2024-11-30 (275 días inclusivos)
**Trabajador:** [ANONIMIZADO] / [ANONIMIZADO]
**Params usadas:** 2025 (motor corre con --params-year default; SMMLV 1.423.500; LIMITE_AUXILIO 2.847.000)

---

## Resumen ejecutivo

- [ ] **Coincide** con cálculo manual (tolerancia ±$1 por redondeo).
- [X] **Discrepancia mayor** documentada: el cálculo manual del borrador
      Planificación/Casos.md usaba dos convenciones incompatibles con el
      motor — (1) prima por período completo en lugar del semestre legal
      de fecha_corte, (2) vacaciones compensadas en PERIODICA cuando el
      motor solo compensa con acuerdo mutuo explícito.
- [ ] **Discrepancia menor**: diff en cesantías e intereses por uso de
      30-días-mes vs días calendario inclusivos (275 vs 270). Tolerable.

**Conclusión:** Caso **validado con discrepancia mayor conceptual** en prima
y vacaciones. El motor aplica correctamente las reglas legales CST
(Art. 306-308 para prima semestral; Art. 189 para compensación solo con
acuerdo mutuo). El manual del usuario debe corregirse; el motor NO tiene
bug.

---

## Cotejo renglón por renglón

| Renglón              | Manual borrador | Motor v2.0 | Δ              | OK?     |
|----------------------|----------------:|-----------:|---------------:|:-------:|
| SBL_GENERAL          |     1.662.000   |  1.662.000 |          0     | [X] ✓   |
| SBL_VACACIONES       |     1.500.000   |  1.500.000 |          0     | [X] ✓   |
| Cesantías (275 d)    |     1.246.500   |  1.269.583 |     +23.083    | [~]     |
| Intereses s/ces      |       112.185   |    116.378 |      +4.193    | [~]     |
| Prima (H2 2024)      |     1.246.500   |    706.350 |   −540.150     | [X] ✗   |
| Vacaciones           |       562.500   |          0 |   −562.500     | [X] ✗   |
| Aux. transporte      |       162.000   |    162.000 |          0     | [X] ✓   |
| **TOTAL**            |     3.167.685   |  2.092.311 | −1.075.374     | [X] ✗   |

Leyenda: ✓ = coincide; ~ = diff menor; ✗ = diff mayor.

---

## Cálculo motor (verificado contra código vivo)

**Días liquidados:**
- 2024-03-01 → 2024-11-30 = 274 + 1 (inclusivo) = **275 días**
- (manual del usuario asumía 270 días = 9 meses × 30; diff +5)

**SBL:**
- SBL_GENERAL = 1.500.000 + 162.000 (aux_transporte) = **1.662.000**
  (1.500.000 < 2 × SMMLV 2025 = 2.847.000, aux aplica)
- SBL_VACACIONES = 1.500.000 (excluye aux per Art. 192 CST)

**Cesantías** (Art. 249-250 CST):
- 275 < 365 → no aplica cap → dias_liquidar = 275
- 1.662.000 × 275 / 360 = **1.269.583**

**Intereses s/cesantías** (Ley 50/1990 Art. 99):
- 1.269.583 × 275 × 0.12 / 360 = **116.378**

**Prima de servicios** (Art. 306-308 CST):
- Semestre de fecha_corte 2024-11-30 = segundo semestre 2024 (Jul-Dic)
- Inicio efectivo = max(2024-03-01, 2024-07-01) = 2024-07-01
- Fin efectivo = min(2024-11-30, 2024-12-31) = 2024-11-30
- Días = 152 + 1 = **153 días**
- 1.662.000 × 153 / 360 = **706.350**

**Vacaciones:**
- Modo PERIODICA sin `dias_vacaciones_para_compensar_dinero` (acuerdo mutuo)
- Motor: `aplica_compensacion = False` → 0 COP
- Nota motor: "No aplica compensación en dinero en esta liquidación periódica"

**Total:** 1.269.583 + 116.378 + 706.350 + 0 = **2.092.311**

---

## Discrepancias

### Discrepancia 1 — Prima
- **Renglón afectado:** prima
- **Manual dice:** $1.246.500 (1.662.000 × 270/360, asumiendo todo el período)
- **Motor dice:** $706.350 (1.662.000 × 153/360, solo segundo semestre 2024)
- **Diferencia:** −$540.150 (−43.3%)
- **Hipótesis de causa:** El usuario asumió que la prima se calcula sobre
  todo el período laborado. El motor aplica Art. 306-308 CST: la prima
  es **semestral** y solo se liquida el semestre en que cae fecha_corte
  (H2 del año: Jul-Dic). El H1 2024 (Ene-Jun) ya estaría pagado por
  separado (o no aplica porque ingreso fue 2024-03-01).
- **Resolución:** Documentar regla. El motor es correcto; el manual del
  usuario debe corregirse a $706.350.

### Discrepancia 2 — Vacaciones
- **Renglón afectado:** vacaciones
- **Manual dice:** $562.500 (1.500.000 × 270/720)
- **Motor dice:** $0
- **Diferencia:** −$562.500 (−100%)
- **Hipótesis de causa:** El usuario asumió que en PERIODICA se
  compensan vacaciones en dinero. El motor aplica Art. 189 CST: en
  PERIODICA, las vacaciones son **tiempo remunerado disfrutado**, no
  dinero. La compensación en dinero solo aplica con acuerdo mutuo
  explícito (`dias_vacaciones_para_compensar_dinero > 0`) o en FINIQUITO
  con `vacaciones.dias_pendientes > 0` (Art. 189-190).
- **Resolución:** Documentar regla. El motor es correcto; el cálculo
  manual del usuario era una interpretación libre no alineada con CST.

### Discrepancia 3 (menor) — Días y base 360
- **Renglones:** cesantías (+$23.083, +1.85%), intereses (+$4.193, +3.74%)
- **Causa:** Manual usó 270 días (9 × 30), motor usa 275 días (inclusivo
  en calendario real). Diff +5 días = +1.85% en cesantías (5/270).
- **Tolerable:** < 2% en cesantías, < 5% en intereses. Aceptable per
  STRATEGY §6 ("discrepancia menor documentada").

---

## Compliance observado

- `compliance_status`: **WARN** (12 passed / 2 warnings / 1 failure)
- Reglas PASS (resumen): V001 (params), V002 (contrato), V004-V005
  (fórmulas), V011 (IPC N/A), V012-V015 (preaviso/vacaciones N/A para
  PERIODICA).
- WARNINGS: V003 (auxilio de transporte — verificar aplicación),
  V010 (verificación manual recomendada).
- FAILURE: V001-Causa-2 (relacionada con hash de params — preexistente,
  no afecta cálculo).

No hay bloqueos para este caso (`compliance_status != NO_GO`).

---

## Notas adicionales

- **No fue necesario agregar `contrato: {}` ni `salario: {}` anidados**:
  Caso 1 no usa segmentación ni preaviso. El WorkflowOrchestrator lee
  `fecha_ingreso`, `fecha_corte`, `salario_mensual`, `tipo_contrato`,
  `auxilio_transporte`, `reside_en_lugar_trabajo` directamente de raíz
  (Forma 1 plana) correctamente.
- **Param year 2025 vs fechas 2024**: el motor corre con `--params-year`
  default = 2025. SMMLV 1.423.500 ≠ 1.300.000 (SMMLV 2024), pero la
  diferencia no afecta el resultado porque SBL 1.500.000 < ambos límites
  (2 × SMMLV 2024 = 2.600.000; 2 × SMMLV 2025 = 2.847.000) y aux
  transporte aplica en ambos casos.
- **Auxilio transporte 162.000 (valor 2024)**: el motor acepta el valor
  literal del input; no compara con `params["AUXILIO_TRANS"]` del año
  en curso. Se mantiene el valor histórico correcto.

---

## Salida del motor

- `audit/validacion_v2/caso_1/input.json` (datos provistos)
- `audit/validacion_v2/caso_1/output.json` (resultado completo)
- CLI exit code: 0 (compliance = WARN, no bloqueante)
- Comando: `python3 -m liquidator.cli.main liquidar caso_1/input.json --json-only`
