# Estrategia 4.F — 3 Liquidaciones Reales (Plan y criterios)

> **Sesión que dejó este documento listo:** S47 (2026-06-18, planning).
> **Próxima acción del usuario:** elegir 3 liquidaciones reales de su
> operación y completar los 3 `input.json` siguiendo esta estrategia.
> **Origen del plan:** conversación S47 opción C ("plan primero antes de
> tocar nada"). Decisión de perfil de cobertura: Básico + Avanzado +
> Complejo.

---

## 1. Por qué 3 liquidaciones reales (no más, no menos)

`Contexto/diagnostico_liquidacion_cli_2026-06-09.md` §6.8 punto 5
exige que el usuario haya ejecutado **al menos 3 liquidaciones reales**
y los resultados coincidan con cálculos manuales o con otra herramienta
de referencia. Es el DoD (Definition of Done) del plan completo de
v2.0: sin esto, Fase 4 no se cierra formalmente.

**Por qué reales, no sintéticas:** los ~650 tests sintéticos + el caso
canónico + 4 golden files YA validan el motor contra sí mismo o contra
fórmulas teóricas. Las 3 liquidaciones reales son la ÚNICA instancia
donde un humano (Jhond) valida que los números cuadran contra su
operación real. Como §6.9 dice: "no hay validación externa" (ni
contador, ni abogado, ni auditor). Estas 3 son ese "doble check
humano" del sistema.

**Por qué exactamente 3:** número mínimo para cubrir (a) caso típico
(baseline), (b) feature nueva (Addendum SL2630-2024), (c) stress
compuesto (compliance + IPC + segmentación). Más de 3 no aporta
cobertura proporcional al esfuerzo.

---

## 2. Perfil de los 3 casos (complementarios, no duplicados)

El set está diseñado para NO solaparse con los golden files
existentes en `examples/inputs/`:

| Golden existente                     | Feature cubierta         | NO se duplica con… |
|--------------------------------------|--------------------------|---------------------|
| `caso_canonico_periodico_206d.json`  | PERIODICA 206d, 2 seg.   | Caso 1 (sin cruce)  |
| `finiquito_renuncia_212d.json`       | FINIQUITO renuncia       | Caso 2 (motivo≠)    |
| `finiquito_fijo_vencido_preaviso`    | FINIQUITO FIJO+preaviso  | Caso 2 o 3 (mixto)  |
| `prescripcion_indexada.json`         | IPC 1 periodo            | Caso 3 (varios)     |

### Caso 1 — "Básico" (smoke test del mundo real)

- **Modo:** `PERIODICA`
- **Tipo contrato:** `INDEFINIDO`
- **Perfil de fechas:** fecha de ingreso **≠ día 16** (el caso canónico
  ES día 16, esto es deliberadamente distinto). Fecha de corte que
  **NO cruce 1-Ene** (para NO ejercitar segmentación — la cubrimos
  en caso 3).
- **SBL:** constante, sin cambios mid-periodo.
- **Aux. transporte:** NO (SBL > 2 × SMMLV, o se decide no pagar).
- **Features a ejercitar:** cálculo proporcional de cesantías, prima,
  vacaciones, intereses. **Sin** salario variable, **sin** IPC,
  **sin** vacaciones compensadas, **sin** segmentación.
- **Por qué este caso:** valida que el "camino feliz" del motor
  produce exactamente lo que vos ya calculaste a mano. Si esto falla,
  hay bug grueso. **No debe sorprender**, pero el valor es descartar
  regresiones en el flujo principal.

### Caso 2 — "Avanzado" (Addendum SL2630-2024 end-to-end)

- **Modo:** `FINIQUITO`
- **Tipo contrato:** `INDEFINIDO` o `FIJO` (vos elegís, ambos son válidos).
- **Perfil de fechas:** contrato **mayor a 1 año** (ej: 2-3 años) y
  con **cambio de SBL mid-periodo** documentado (ej: SBL 2.000.000 en
  2024 → 2.300.000 en 2025 → 2.500.000 en 2026).
- **Vacaciones pendientes:** > 0 (ej: 8.5 días), para que el motor
  calcule vacaciones compensadas en finiquito.
- **Aux. transporte:** SÍ (con SBL cercano al umbral SMMLV × 2 para
  ejercitar el caso condicional).
- **Motivo de terminación:** `renuncia_voluntaria` o
  `mutuo_acuerdo` (descarta indemnización Art. 64 — R-LEG-01).
- **Features a ejercitar:**
  - `Salario.historial_salarial` o `Salario.sbl_por_anio`
    (anualización por año calendario, Addendum SL2630-2024).
  - `VacacionesEstado.dias_pendientes` + cálculo Art. 189-190 CST
    (vacaciones compensadas en finiquito).
  - `Salario.auxilio_transporte` condicional según SMMLV vigente del año.
- **Por qué este caso:** es la **única validación end-to-end** del
  Addendum SL2630-2024 contra datos reales. El schema está
  implementado (1.C-bis S23, 2.B-bis S27) pero no hay golden file
  end-to-end con salario variable. Esto llena ese hueco.

### Caso 3 — "Complejo" (IPC + compliance compuesta)

- **Modo:** `FINIQUITO`
- **Tipo contrato:** `INDEFINIDO` (más simple) o `FIJO` (con preaviso).
- **Perfil de fechas:** contrato **mayor a 1 año** y con
  **cruce de 1-Ene** (ej: ingreso 2024-03-15, terminación 2026-07-20)
  → ejercita segmentación 2024 + 2025 + 2026.
- **Periodos no pagados:** **1 o más** prestaciones de años anteriores
  NO pagadas oportunamente (ej: prima de servicios 2023-H2 + cesantías
  2024). Esto activa la indexación IPC (Addendum SL2630-2024 +
  Art. 488 CST, Tarea 2.X).
- **Preaviso (si FIJO):** declarar `preaviso_entregado` (True o False)
  + `dias_preaviso` para que el motor calcule indemnización Art. 46 CST.
- **Vacaciones pendientes:** 0 (para mantener foco en IPC, no en
  vacaciones compensadas).
- **Features a ejercitar:**
  - `periodos_no_pagados` con `PeriodoNoPagado` (varios simultáneos).
  - Indexación IPC con `IPCIndexador` (Tarea 2.X S28).
  - Validación de prescripción Art. 488 CST (3 años desde
    `fecha_exigibilidad`).
  - Segmentación multi-año con 3+ segmentos (2024 + 2025 + 2026).
  - Si FIJO: regla de preaviso + cálculo indemnización Art. 46.
  - Compliance V011 (V_INDEXACION_IPC, MEDIUM no-bloqueante) +
    V012-V015 (finiquito + vacaciones) → stress test de reglas
    compuestas.
- **Por qué este caso:** ejercita el feature **más nuevo y menos
  probado** del motor (IPC + prescripción). Cualquier bug en la
  cadena `PeriodoNoPagado → IPCIndexador → compliance V011 → output`
  aparece acá. Es el caso con mayor densidad de features por línea
  de input.

---

## 3. Datos que vos necesitás proveer (formulario por caso)

Para cada caso, los **mínimos** que necesito son estos. Con eso +
vuestro cálculo manual, podemos producir el input.json, correr el
CLI, y llenar la comparativa.

### Caso 1 — Básico

```
- nombre_o_alias:        __________________  (anónimo o real)
- fecha_ingreso:         ____-__-__          (≠ día 16)
- fecha_corte:           ____-__-__          (mismo año que fecha_ingreso)
- salario_mensual:       __________________  COP
- aux_transporte:        [ ] sí   [x] no
- cálculo manual previo: [ ] sí   [ ] no
  si sí, valores esperados por renglón:
    - cesantías:         __________________
    - prima:             __________________
    - vacaciones:        __________________
    - intereses_s/ces:   __________________
    - total:             __________________
```

### Caso 2 — Avanzado

```
- nombre_o_alias:        __________________
- fecha_ingreso:         ____-__-__
- fecha_terminacion:     ____-__-__
- tipo_contrato:         [ ] INDEFINIDO   [ ] FIJO
- motivo_terminacion:    __________________ (renuncia_voluntaria, mutuo_acuerdo, etc.)
- SBL por año (cambios):
    - año ____: SBL _____________ (meses afectados: ____-____)
    - año ____: SBL _____________ (meses afectados: ____-____)
    - año ____: SBL _____________ (meses afectados: ____-____)
- aux_transporte:        [ ] sí   [ ] no
- vacaciones_pendientes_dias: ____.__
- cálculo manual previo: [ ] sí   [ ] no
  si sí, valores esperados:
    - cesantías_total:   __________________
    - intereses_total:   __________________
    - prima_total:       __________________
    - vacaciones_compensadas: _____________
    - aux_transporte_total: _____________
    - total_finiquito:   __________________
```

### Caso 3 — Complejo

```
- nombre_o_alias:        __________________
- fecha_ingreso:         ____-__-__
- fecha_terminacion:     ____-__-__
- tipo_contrato:         [ ] INDEFINIDO   [ ] FIJO
- motivo_terminacion:    __________________
- SBL por año (constante o cambios):  __________________
- periodos_no_pagados (1 o más):
    - prestación 1:
        * concepto:    __________________ (cesantias / prima / intereses_cesantias / vacaciones)
        * valor_original: _____________
        * fecha_causacion: ____-__-__
        * fecha_exigibilidad: ____-__-__
        * fecha_referencia_indexacion: ____-__-__
    - prestación 2 (opcional): … (mismos campos)
- vacaciones_pendientes_dias: 0
- cálculo manual previo: [ ] sí   [ ] no
  si sí, valores esperados:
    - cesantías (segmentadas):   __________________
    - prima (segmentada):       __________________
    - periodos indexados VA:    __________________
    - total_finiquito:          __________________
```

---

## 4. Procedimiento de ejecución (comandos exactos)

Por cada caso, una vez con el `input.json` lleno:

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli

# 4.1 Validar schema del input (catches errores antes de motor)
PYTHONPATH=. uv run --with click --with pydantic --with loguru \
  python3 -m liquidator.cli.main validate \
  audit/validacion_v2/caso_N/input.json

# 4.2 Correr liquidación
PYTHONPATH=. uv run --with click --with pydantic --with loguru \
  --with python-dateutil --with Jinja2 --with markdown \
  python3 -m liquidator.cli.main liquidar \
  audit/validacion_v2/caso_N/input.json --json-only \
  --out-dir audit/validacion_v2/caso_N

# 4.3 Generar artefactos humanos (md + pdf) — solo si compliance = GO
PYTHONPATH=. uv run --with click --with pydantic --with loguru \
  --with python-dateutil --with Jinja2 --with markdown \
  python3 -m liquidator.cli.main liquidar \
  audit/validacion_v2/caso_N/input.json \
  --out-dir audit/validacion_v2/caso_N
```

**Output esperado por caso** (en `audit/validacion_v2/caso_N/`):
- `input.json` — el input provisto (vos lo llenás).
- `output.json` — output completo del motor (generado por CLI).
- `liquidacion.md` — render humano (solo si compliance = GO).
- `liquidacion.pdf` — PDF (solo si compliance = GO).
- `liquidacion_BLOQUEADA.json` + `liquidacion_BLOQUEADA.md` — si
  compliance = NO_GO (sin PDF por AGENTS.md #7).
- `comparativa.md` — vuestro cotejo motor vs manual (vos lo llenás).
- `notas.md` — observaciones adicionales (vos lo llenás).

---

## 5. Template de `comparativa.md`

```markdown
# Caso N — [Nombre o alias]

**Fecha de ejecución:** ____-__-__
**Modo:** PERIODICA | FINIQUITO
**Tipo contrato:** INDEFINIDO | FIJO | OBRA_LABOR | PRESTACION
**Período:** ____-__-__ → ____-__-__ (___ días)

## Resumen ejecutivo

- [ ] **Coincide** con cálculo manual (tolerancia ±$1 por redondeo).
- [ ] **Discrepancia menor** documentada (ej: diferencia < 1% por
      [aux_transporte_no_pago_por_X, etc.]).
- [ ] **Discrepancia mayor** que requiere corrección del motor.

## Cotejo renglón por renglón

| Renglón              | Motor v2.0 | Cálculo manual | Δ       | OK? |
|----------------------|-----------:|---------------:|--------:|:---:|
| Cesantías            | $_________ | $_________     | $______ | [ ] |
| Intereses s/cesantías| $_________ | $_________     | $______ | [ ] |
| Prima                | $_________ | $_________     | $______ | [ ] |
| Vacaciones           | $_________ | $_________     | $______ | [ ] |
| Vacaciones comp.     | $_________ | $_________     | $______ | [ ] |
| Indemnización preaviso| $_________| $_________     | $______ | [ ] |
| Aux. transporte      | $_________ | $_________     | $______ | [ ] |
| Indexación IPC VA    | $_________ | $_________     | $______ | [ ] |
| **TOTAL**            | $_________ | $_________     | $______ | [ ] |

## Compliance observado

- `compliance_status`: GO | WARN | NO_GO | OVERRIDE_APPROVED
- Reglas disparadas (si las hay): V0XX, V0YY, …
- Bloqueos (si los hay): …

## Discrepancias (si las hay)

### Discrepancia 1
- **Renglón afectado:** ____
- **Motor dice:** $______
- **Manual dice:** $______
- **Diferencia:** $______ (X.XX%)
- **Hipótesis de causa:** …
- **Issue abierta:** [link o número]

## Conclusión

[Una línea: "Caso validado, sin discrepancias" o "Caso validado con
discrepancia menor X" o "Caso NO validado, requiere fix de motor Y".]
```

---

## 6. Procedimiento ante discrepancia

**Regla de §6.8 / plan §9.2:** si hay **cualquier discrepancia** entre
motor y cálculo manual, **NO se cierra Fase 4**. Procedimiento:

1. **Documentar** la discrepancia en `comparativa.md` con hipótesis.
2. **Abrir issue** con:
   - Caso (audit/validacion_v2/caso_N/)
   - Renglón afectado
   - Diff exacto (motor vs manual)
   - Hipótesis de causa
3. **Decidir triage** (en sesión de fix dedicada):
   - Bug del motor → fix en código + agregar test regresivo.
   - Error del input (mío al armar el JSON) → corregir input, re-correr.
   - Cálculo manual obsoleto (usaste fórmula vieja) → actualizar
     cálculo manual, no es bug del motor.
4. **Re-correr** el caso hasta que coincida.
5. **Cerrar** el issue y la entrada de comparativa.md.

**Si las 3 coinciden:** tarea 4.F cerrada. Fase 4 formalmente cerrada.
Plan v2.0 completo = DONE.

---

## 7. Out of scope (no son parte de la validación)

Por diseño, las 3 liquidaciones reales **no validan** lo siguiente (ya
cubierto por otros medios o explícitamente fuera de v2.0):

- **Indemnización Art. 64 CST** (despido sin justa causa) →
  R-LEG-01: NO implementada en v2.0. El output trae
  `indemnizacion: null`. Si tu caso real es un despido sin justa
  causa, **no va a coincidir** el renglón indemnización. Documentar
  como esperado y elegir otro motivo de terminación para los casos
  de prueba.
- **Pago mensual de intereses sobre cesantías** (R-LEG-06): el plan
  v2.0 lo atribuyó a Art. 64 Ley 2466/2025, pero SUIN refutó esa
  atribución. NO implementado. No incluir en cálculos manuales.
- **Recargo dominical / horas extra / nocturno**: features fuera del
  alcance de las 3 liquidaciones de validación. Si querés validar,
  eso es Fase 5 (opcional).
- **Liquidaciones con más de 5 años de servicio**: el motor soporta,
  pero la cobertura de tests sintéticos es < 1 año. Si tu caso real
  tiene > 5 años, es buena señal (no probado mucho) → incluirlo
  aumenta valor.

---

## 8. Cierre (qué pasa cuando los 3 casos coinciden)

Una vez los 3 `comparativa.md` muestran coincidencia (o discrepancia
documentada y corregida):

1. **Actualizar `Planificación/REGISTRY.md`** — marcar Tarea 4.F como
   CERRADA, mover Fase 4 a CERRADA.
2. **Actualizar `Planificación/REGISTRY_LOG.md`** — entrada SXX con
   evidencia (commits, archivos, output hashes).
3. **Agregar entrada en `CHANGELOG.md`** bajo `## [Unreleased]` o
   crear `## [2.0.1]` si hay fix.
4. **Opcional:** re-tageo `v2.0.0` con `--amend` o nuevo `v2.0.1` con
   los fixes de las discrepancias.
5. **Plan v2.0 completo = DONE.**

---

## 9. Handoff a nueva sesión

Si retomás en una sesión futura, los 6 pasos son:

1. Leer este `STRATEGY.md` (5 min).
2. Releer `Planificación/REGISTRY.md` "Estado actual" + "Bloqueos
   activos" + "Trampas conocidas" (5 min).
3. Releer `audit/validacion_v2/README.md` (3 min).
4. Elegir uno de los 3 casos (Básico recomendado para arrancar).
5. Llenar el `input.json` correspondiente siguiendo §3 de este doc.
6. Correr el comando de §4.

Total: ~15 min para retomar.
