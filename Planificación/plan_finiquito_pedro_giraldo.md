# PLAN — Liquidación Finiquito: Pedro Luis Giraldo Franco

> **Estado:** BLOQUEADO — Esperando 3 respuestas de Jhond antes de ejecutar
> **Creado:** 2026-06-23
> **Motor:** v2.0.0
> **Motivo ejecución:** Renuncia voluntaria, último día 2026-07-15

---

## ⛔ GATE DE EJECUCIÓN — Responder ANTES de iniciar

> **Este plan NO puede ejecutarse hasta que las 3 preguntas de abajo
> tengan respuesta confirmada.** El agente debe leer esta sección
> primero y verificar que las 3 respuestas existan antes de proceder
> al Paso 2. Si falta alguna → detener y preguntar al usuario.

### PREGUNTA 1 — Discrepancia liquidación previa

La liquidación PERIODICA v1.0.0 ($2,630,000) usó SBL=$1,500,000.
Con el SBL corregido (SMMLV+ordeño = $1,723,500), debió ser ~$3,022,413.
Diferencia: ~$392,413 a favor del trabajador.

**Pregunta:** ¿Se debe reliquidar el período previo (2024-11-16 →
2025-11-15) con el SBL corregido?

| Opción | Descripción | Impacto |
|--------|-------------|---------|
| A | Solo liquidar el finiquito (NO reliquidar previo) | Finiquito ~$2.1M |
| B | Reliquidar previo + finiquito por separado | Previo ~$392K + Finiquito ~$2.1M |
| C | Liquidar TODO el período de golpe como finiquito | Un solo cálculo, 607 días |

**Respuesta de Jhond:** `[PENDIENTE]`

### PREGUNTA 2 — Forma del input (segmentación)

El período cruza 1-Ene-2026 (45d en 2025 + 196d en 2026). El motor
v2.0.0 segmenta por año con SL2630-2024, pero necesita saber el SBL
de cada año.

**Pregunta:** ¿Qué formato de input usar?

| Opción | Descripción | Ventaja | Riesgo |
|--------|-------------|---------|--------|
| A | Forma 1 plana con `salario_mensual: 2050905` | Simple | Motor puede no segmentar SBL por año (usa mismo SBL para ambos) |
| B | Forma 2 con `sbl_por_anio: {"2025": 1723500, "2026": 2050905}` | Segmentación correcta por año | Requiere verificar compatibilidad con Forma 1 plana en WorkflowOrchestrator |
| C | Forma 1 con `historial_salarial` | Más preciso | Más complejo de armar |

**Respuesta de Jhond:** `[PENDIENTE]`

### PREGUNTA 3 — Fecha de ejecución

**Pregunta:** ¿Cuándo se ejecuta la liquidación?

| Opción | Descripción | Consideración |
|--------|-------------|---------------|
| A | Ahora (antes del 15-jul) | fecha_corte = hoy, días parciales de junio |
| B | El 15-jul o después | fecha_corte = 2026-07-15, período completo |

**Respuesta de Jhond:** `[PENDIENTE]`

---

> **REGLA:** Si el agente intenta ejecutar el Paso 2 (armar input.json)
> sin que las 3 respuestas estén confirmadas → DETENER y solicitar
> las respuestas pendientes al usuario.

---
## 1. Datos del trabajador (confirmados por Jhond)

```yaml
trabajador:
  nombre: "PEDRO LUIS GIRALDO FRANCO"     # PII — repo privado
  documento: "7.247.867"                    # PII — repo privado
  fecha_ingreso: "2024-11-16"
  fecha_corte: "2026-07-15"                 # último día trabajado
  tipo_contrato: "INDEFINIDO"
  motivo_terminacion: "renuncia_voluntaria"
  fecha_terminacion_real: "2026-07-15"
  reside_en_lugar_trabajo: true             # sin auxilio transporte
  predio: "Lote 1 El Venado + Lote 2 La Isabella II, Santa Rosa de Cabal"
```

## 2. Datos salariales (confirmados por Jhond)

```yaml
salario:
  smmlv_2025: 1_423_500
  smmlv_2026: 1_750_905
  compensacion_ordeño_festivos: 300_000    # salario habitual (Art. 127 CST)
  compensacion_energia: 55_000             # reembolso gasto — NO entra al SBL
  vive_en_finca: true                      # sin auxilio transporte
```

### SBL por año (segmentación SL2630-2024)

| Concepto | 2025 | 2026 |
|----------|------|------|
| SMMLV | $1,423,500 | $1,750,905 |
| Ordeño festivos | $300,000 | $300,000 |
| **SBL mensual** | **$1,723,500** | **$2,050,905** |
| Energía | excluida (reembolso) | excluida (reembolso) |
| Auxilio transporte | excluido (reside en finca) | excluido (reside en finca) |

> **NOTA LEGAL:** La compensación de ordeño dominical/festivo es pago habitual
> mensual fijo → constituye salario según Art. 127 CST. Se incluye en el SBL.
> La energía ($55,000) es reembolso de gasto → NO es salario.

## 3. Liquidación previa (ya pagada)

```yaml
liquidacion_previa:
  modo: "PERIODICA"
  periodo: "2024-11-16 → 2025-11-15"    # 365 días
  sbl_usado: 1_500_000
  total_pagado: 2_630_000
  fecha_generacion: "2025-12-02"
  archivo: "output/_legacy/liquidacion_pedro_franco.json"
  estado: "PAGADA"                       # Jhond confirmó pago
```

### Discrepancia detectada con liquidación previa

La liquidación PERIODICA v1.0.0 usó SBL = $1,500,000. Con la información
actualizada (ordeño = salario habitual), el SBL correcto de 2025 era
$1,723,500. Esto implica que la liquidación previa quedó **subvalorada**.

| Concepto | Liquidado v1.0.0 | Correcto (SBL $1,723,500) | Diferencia |
|----------|------------------|---------------------------|------------|
| Cesantías (365d) | $1,500,000 | $1,723,750 | +$223,750 |
| Intereses (12%) | $180,000 | $206,850 | +$26,850 |
| Prima (138d H2) | $575,000 | $660,938 | +$85,938 |
| Vacaciones (7.5d) | $375,000 | $430,875 | +$55,875 |
| **TOTAL** | **$2,630,000** | **$3,022,413** | **+$392,413** |

> **ACCIÓN REQUERIDA:** Evaluar si se debe reliquidar el período 2024-11-16 →
> 2025-11-15 con el SBL corregido ($1,723,500). Esto es independiente de la
> liquidación de finiquito. Decisión del usuario.

## 4. Período a liquidar (finiquito)

La liquidación previa cubrió hasta 2025-11-15. El finiquito cubre el
período restante hasta la terminación.

```yaml
periodo_finiquito:
  desde: "2025-11-16"      # día siguiente a la liquidación previa
  hasta: "2026-07-15"      # último día trabajado
  dias_totales: 241         # inclusivo

  # Segmentación por año calendario (SL2630-2024)
  segmento_2025:
    desde: "2025-11-16"
    hasta: "2025-12-31"
    dias: 46
    sbl: 1_723_500

  segmento_2026:
    desde: "2026-01-01"
    hasta: "2026-07-15"
    dias: 196
    sbl: 2_050_905
```

## 5. Estimación de cálculo (pre-ejecución)

### Cesantías (Art. 249-250 CST)

| Segmento | SBL | Días | Fórmula | Valor estimado |
|----------|-----|------|---------|---------------|
| 2025 | $1,723,500 | 46 | SBL × (dias/360) | $220,983 |
| 2026 | $2,050,905 | 196 | SBL × (dias/360) | $1,117,937 |
| **Total cesantías** | | | | **~$1,338,920** |

### Intereses cesantías (Ley 50/1990 Art. 99 — 12% anual)

| Concepto | Fórmula | Valor estimado |
|----------|---------|---------------|
| Intereses | Cesantías_totales × 12% × (241/360) | ~$107,653 |

### Prima de servicios (Art. 306-308 CST)

| Semestre | SBL | Días | Fórmula | Valor estimado |
|----------|-----|------|---------|---------------|
| H2-2025 (16-nov a 31-dic) | $1,723,500 | 46 | SBL × (dias/360) / 2 | $110,492 |
| H1-2026 (1-ene a 15-jul) | $2,050,905 | 196 | SBL × (dias/360) / 2 | $558,969 |
| **Total prima** | | | | **~$669,461** |

### Vacaciones compensadas (Art. 189-190 CST)

```yaml
vacaciones:
  dias_pendientes: 0        # ya disfrutados (confirmado por Jhond)
  valor_compensado: 0       # sin compensación pendiente
```

### Indemnización Art. 64 CST

```yaml
indemnizacion:
  aplica: NO                # renuncia voluntaria → Art. 49.6 CST
  valor: null
```

### Total estimado

| Concepto | Valor estimado |
|----------|---------------|
| Cesantías | ~$1,338,920 |
| Intereses cesantías | ~$107,653 |
| Prima proporcional | ~$669,461 |
| Vacaciones compensadas | $0 |
| Indemnización | N/A |
| **TOTAL ESTIMADO** | **~$2,116,034** |

> **IMPORTANTE:** Estos valores son ESTIMACIONES manuales. El motor v2.0.0
> es la fuente de verdad. Puede haber diferencias por redondeo (ROUND_HALF_UP),
> días inclusivos, y cálculo exacto de intereses por segmento.

## 6. Input JSON (a generar en Paso 2)

```json
{
  "modo": "FINIQUITO",
  "fecha_ingreso": "2024-11-16",
  "fecha_corte": "2026-07-15",
  "salario_mensual": 2050905,
  "tipo_contrato": "INDEFINIDO",
  "motivo_terminacion": "renuncia_voluntaria",
  "fecha_terminacion_real": "2026-07-15",
  "vacaciones": {
    "dias_pendientes": 0,
    "dias_disfrutados": 15
  },
  "trabajador": {
    "nombre": "PEDRO LUIS GIRALDO FRANCO",
    "documento": "7.247.867"
  },
  "empleador": {
    "nombre": "HILDA LIRIA RAIGOZA LOAIZA",
    "documento": "42066783"
  },
  "_notas": {
    "sbl_2025": 1723500,
    "sbl_2026": 2050905,
    "vive_en_lugar_trabajo": true,
    "energia_es_reembolso": true,
    "liquidacion_previa_pagada": true,
    "periodo_previo": "2024-11-16 a 2025-11-15"
  }
}
```

> **NOTA:** `salario_mensual` = 2,050,905 (SBL 2026). Para la segmentación
> correcta del período 2025 vs 2026, el motor debería usar el SBL por año.
> Si el WorkflowOrchestrator no soporta SBL por año con Forma 1 plana,
> habrá que usar `sbl_por_anio` o `historial_salarial` (Forma 2 extendida).
> Evaluar al ejecutar.

## 7. Compliance esperado

| Regla | Resultado esperado | Razón |
|-------|-------------------|-------|
| V001 | PASS | Params 2025+2026 presentes |
| V002 | PASS | Contrato INDEFINIDO válido |
| V003 | PASS | Auxilio excluido (reside en finca) |
| V004 | PASS | Fórmulas cesantías correctas |
| V005 | PASS | Tasa 12% |
| V006 | WARN | Período no coincide con semestre exacto |
| V007 | PASS | Vacaciones manejadas en finiquito |
| V008 | PASS | Plazos documentados |
| V009 | PASS | Sustento legal presente |
| V010 | PASS | Hashes y versionamiento |
| V011 | PASS | Sin periodos_no_pagados (opt-in) |
| V012 | PASS | No aplica (INDEFINIDO, no FIJO) |
| V013 | PASS | No aplica (INDEFINIDO) |
| V014 | PASS | dias_pendientes=0, sin compensación necesaria |
| V015 | PASS | Vacaciones declaradas (0 pendientes) |

**Status esperado:** GO (sin blocking failures)

## 8. Preguntas pendientes

> **Ver sección `⛔ GATE DE EJECUCIÓN` al inicio del documento.**
> Las 3 preguntas con opciones están allí. El plan está BLOQUEADO
> hasta que las 3 tengan respuesta confirmada.

---

## Estado de ejecución

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1 | Confirmar datos (gaps 1-5) | ✓ COMPLETADO |
| 2 | Armar input.json | PENDIENTE |
| 3 | Ejecutar liquidación | PENDIENTE |
| 4 | Revisión output | PENDIENTE |
| 5 | Entregar artefactos | PENDIENTE |
