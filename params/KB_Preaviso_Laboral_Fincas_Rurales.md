# KB: Preaviso y Liquidación Laboral — Fincas Rurales (Colombia)
> **Versión:** 1.0 · **Corte normativo:** Ley 2466 de 2025 · **Fecha de referencia:** 13 junio 2026  
> **Uso:** Base de conocimiento estructurada para consumo por agente de IA en pipeline de cálculo/asesoría laboral rural.

---

## [INDICE_RAPIDO]

| Necesidad del pipeline | Sección |
|---|---|
| Marco legal aplicable | → `[MARCO_NORMATIVO]` |
| Definición de preaviso | → `[PREAVISO_DEFINICION]` |
| Reglas por tipo de contrato | → `[PREAVISO_POR_MODALIDAD]` |
| ¿Se puede pagar en dinero? | → `[PREAVISO_EJECUCION]` |
| Qué pasa si el empleador omite preaviso | → `[OMISION_EMPLEADOR]` |
| Qué pasa si el trabajador omite preaviso | → `[OMISION_TRABAJADOR]` |
| Tabla de decisión por situación | → `[TABLA_DECISION]` |
| Fórmulas matemáticas de liquidación | → `[FORMULAS_LIQUIDACION]` |
| Variables económicas 2025–2026 | → `[VARIABLES_MACRO]` |
| Cómputo de días trabajados | → `[COMPUTO_DIAS]` |
| Escenario A: empleador con cortes anuales | → `[ESCENARIO_A]` |
| Escenario B: empleador acumulativo | → `[ESCENARIO_B]` |
| Tabla comparativa de escenarios | → `[TABLA_ESCENARIOS]` |
| Plantillas de notificación y cálculo | → `[PLANTILLAS]` |
| Glosario de términos técnicos | → `[GLOSARIO]` |
| Alertas de riesgo legal (prioridades) | → `[ALERTAS_RIESGO]` |

---

## [MARCO_NORMATIVO]

### Jerarquía normativa vigente

```yaml
marco_legal:
  ley_principal: "Ley 2466 de 2025 — Reforma Laboral"
  proposito: "Garantizar trabajo decente, formalización y redefinición de esquemas de contratación"
  regimen_base: "Código Sustantivo del Trabajo (CST) + modificaciones Ley 2466/2025"
  
  articulos_clave:
    - art: "Art. 4 — Ley 2466/2025"
      contenido: "Principio de protección especial al campesinado — sujeto de tutela constitucional"
    - art: "Art. 46 — CST mod. por Ley 2466/2025"
      contenido: "Contrato a término fijo: máx. 4 años, constar por escrito, preaviso 30 días"
    - art: "Art. 47 — CST mod. por Ley 2466/2025"
      contenido: "Contrato indefinido: modalidad preferente; preaviso voluntario de 30 días del trabajador"
    - art: "Art. 48 — CST"
      contenido: "Cláusula de reserva: empleador puede pagar dinero en vez de preaviso en tiempo"
    - art: "Art. 62 — CST"
      contenido: "Causales de despido con justa causa (causales 9-15 requieren 15 días de preaviso)"
    - art: "Art. 64 — CST"
      contenido: "Indemnización por despido sin justa causa"
    - art: "Art. 65 — CST"
      contenido: "Sanción moratoria: 1 día de salario por cada día de retraso en liquidación"

  normas_derogadas_relevantes:
    - "Art. 8, Decreto 2351/1965: descuento de 30 días por renuncia intempestiva → DEROGADO por Art. 28, Ley 789/2002"

  iniciativa_pendiente_no_vinculante:
    nombre: "Proyecto de Ley 504 de 2025 — Contrato y Jornal Laboral Agrario"
    estado: "Primer debate Cámara de Representantes (2026)"
    efecto_juridico: "SIN fuerza vinculante — NO aplicar"

  excepcion_sector_rural:
    aplica: false
    detalle: "La ley NO contempla régimen exceptivo de preaviso para trabajadores de fincas rurales"
    comparacion: "Servicio doméstico y choferes familiares sí tienen régimen especial (7 días, Art. 48 CST)"
```

---

## [PREAVISO_DEFINICION]

**Preaviso:** Manifestación unilateral de voluntad mediante la cual una de las partes comunica a la otra su decisión de terminar el vínculo laboral en una fecha futura determinada.

**Principio rector:** La vigencia del preaviso depende de:
1. La **modalidad contractual** pactada
2. **Quién** toma la iniciativa de disolver el vínculo

---

## [PREAVISO_POR_MODALIDAD]

### Contratos a Término Fijo

```yaml
contrato_termino_fijo:
  norma: "Art. 46 CST mod. Ley 2466/2025"
  requisitos_formales:
    - "Debe constar SIEMPRE por escrito"
    - "Duración máxima: 4 años"
  
  preaviso_empleador:
    obligacion: true
    plazo_dias: 30
    tipo_dias: "calendario"
    forma: "escrito"
    momento: "antes del vencimiento del contrato"
    consecuencia_omision: "prórroga automática por período igual al pactado (por ministerio de la ley)"
  
  preaviso_trabajador:
    obligacion: true
    plazo_dias: 30
    tipo_dias: "calendario"
    forma: "escrito"
    consecuencia_omision: "NINGUNA — el empleador NO puede sancionar ni descontar"
```

### Contratos a Término Indefinido

```yaml
contrato_termino_indefinido:
  norma: "Art. 47 CST mod. Ley 2466/2025"
  modalidad_preferente: true
  
  terminacion_por_empleador:
    preaviso_requerido: false
    excepciones:
      - causales: "Causales 9 a 15 del Art. 62 CST (incapacidad parcial, enfermedad crónica no profesional, etc.)"
        preaviso_dias: 15
        tipo_dias: "calendario"
    sin_justa_causa:
      preaviso_requerido: false
      accion_requerida: "Pagar indemnización Art. 64 CST — sin preaviso previo"
  
  renuncia_trabajador:
    preaviso_voluntario_dias: 30
    tipo_dias: "calendario"
    proposito: "Para que el empleador provea reemplazo"
    consecuencia_omision: "NINGUNA — prohibición categórica de sanción económica bajo Ley 2466/2025"
```

### Contratos por Obra o Labor Determinada

```yaml
contrato_obra_labor:
  preaviso_aplica: false
  terminacion: "Natural e inmediata al concluir la obra o labor específicamente pactada"
  requisito_previo: "La labor debe estar definida por escrito"
  comunicacion_anticipada: "NO requerida"
```

---

## [PREAVISO_EJECUCION]

### Dos formas de ejecutar el preaviso

```yaml
modalidad_en_tiempo:
  descripcion: "La parte notifica respetando los 30 días; el trabajador sigue laborando"
  durante_el_periodo:
    - "Trabajador presta servicios de forma regular"
    - "Se devenga salario ordinario"
    - "Se efectúan aportes a seguridad social"
    - "Se siguen causando prestaciones sociales"
  estado_vinculo: "PLENAMENTE ACTIVO durante los 30 días"

modalidad_en_dinero:
  descripcion: "Empleador rescinde de forma inmediata pagando compensación equivalente"
  instrumento_legal: "Cláusula de Reserva (Art. 48 CST)"
  requisito: "Debe pactarse en el contrato"
  calculo: "Salarios correspondientes a los días de preaviso omitido"
  aplica_solo_a: "Omisión del empleador — NO aplica para omisión del trabajador"
```

---

## [OMISION_EMPLEADOR]

### Contrato a Término Fijo — Omisión de los 30 días de no renovación

> ⚠️ **ALERTA CRÍTICA:** Pagar en dinero los 30 días NO subsana la omisión del preaviso fijo.

```
MITO:   "Puedo pagar 30 días en dinero para compensar no haber notificado a tiempo"
VERDAD: ILEGAL — El contrato YA se prorrogó automáticamente por ministerio de la ley

CONSECUENCIA:
  Si el empleador retira al trabajador después de la prórroga automática
  → Se configura DESPIDO INJUSTIFICADO
  → Obligación de pagar indemnización Art. 64 CST
  → Base = salarios de TODO el período de la nueva prórroga (>> 30 días de preaviso)
```

---

## [OMISION_TRABAJADOR]

### Renuncia sin preaviso (sin 30 días)

```yaml
renuncia_intempestiva:
  regimen_historico_derogado:
    norma: "Art. 8, Decreto 2351/1965"
    permitia: "Descuento de 30 días de salario de la liquidación"
    estado: "DEROGADO por Art. 28, Ley 789/2002"
  
  regimen_vigente_2026:
    norma: "Art. 47 CST + Ley 2466/2025"
    descuento_permitido: false
    retencion_permitida: false
    accion_requerida_empleador: "Pagar liquidación COMPLETA"
    plazo_pago_liquidacion: "5 días hábiles tras terminación (criterio jurisprudencial)"
    sancion_por_incumplimiento: "Art. 65 CST — 1 día de salario por cada día de retraso"
```

---

## [TABLA_DECISION]

| ID Situación | Situación Laboral | Vía Legal | Mecanismo de Pago | Base de Cálculo |
|---|---|---|---|---|
| `SIT_01` | No renovación fijo con preaviso oportuno (≥30 días antes) | Preaviso en tiempo | Salario ordinario por 30 días trabajados + aportes | Salario básico mensual pactado |
| `SIT_02` | Despido antes del vencimiento del fijo (término no cumplido) | Despido sin justa causa | Indemnización Art. 64 CST | Salarios faltantes para el vencimiento pactado |
| `SIT_03` | No renovación fijo SIN preaviso oportuno (<30 días) | Contrato prorrogado + despido injustificado si se retira | Indemnización Art. 64 CST | Salarios del período completo de la prórroga automática |
| `SIT_04` | Renuncia voluntaria sin preaviso de 30 días | Aceptación inmediata — sin sanciones | Liquidación de prestaciones causadas hasta último día trabajado | Salario devengado hasta fecha efectiva de retiro |
| `SIT_05` | Despido indefinido sin justa causa | Despido sin justa causa | Indemnización Art. 64 CST | Según tabla del Art. 64 CST |
| `SIT_06` | Despido indefinido causales 9-15 Art.62 | Despido con justa causa + preaviso 15 días | Sin indemnización; solo prestaciones | Salario básico |
| `SIT_07` | Terminación contrato por obra | Terminación natural | Solo prestaciones causadas | Salario último devengado |

---

## [VARIABLES_MACRO]

```yaml
variables_economicas:
  vigencia_2025:
    smmlv: 1_423_500  # COP
    auxilio_transporte_conectividad: 200_000  # COP
    base_prestacional_total: 1_623_500  # COP (salario + auxilio)
    salario_diario_basico: 47_450  # COP (sin auxilio)
  
  vigencia_2026:
    smmlv: 1_750_905  # COP
    auxilio_transporte_conectividad: 249_095  # COP
    base_prestacional_total: 2_000_000  # COP (salario + auxilio)
    salario_diario_basico: 58_363.50  # COP (sin auxilio)

reglas_base_prestacional:
  incluir_auxilio_en:
    - cesantias        # para trabajadores que devenguen hasta 2 SMMLV
    - prima_servicios  # para trabajadores que devenguen hasta 2 SMMLV
  excluir_auxilio_de:
    - vacaciones       # siempre se calcula solo sobre salario básico ordinario

estandar_calculo:
  dias_por_mes: 30
  dias_por_anio: 360
```

---

## [COMPUTO_DIAS]

### Período de referencia: 16 nov 2025 → 13 jun 2026

```yaml
computo_ejemplo:
  fecha_inicio: "2025-11-16"
  fecha_fin: "2026-06-13"
  total_dias: 208

  desglose:
    vigencia_2025:
      dias: 45
      detalle:
        noviembre: 15  # del 16 al 30
        diciembre: 30
    vigencia_2026:
      dias: 163
      detalle:
        enero_a_mayo: 150  # 5 meses × 30 días
        junio: 13          # del 1 al 13

formula_dias_entre_fechas: |
  Para cualquier período:
  dias_mes_parcial_inicio = 30 - (dia_inicio - 1)
  dias_meses_completos    = meses_completos × 30
  dias_mes_parcial_fin    = dia_fin
  total                   = suma de los tres componentes
```

---

## [FORMULAS_LIQUIDACION]

### Fórmulas matemáticas laborales colombianas

> Estándar: meses de 30 días, años de 360 días.

```
CESANTÍAS (C):
  C = (Salario_Base_Mensual × Días_Laborados) / 360

INTERESES SOBRE CESANTÍAS (IC):
  IC = (Cesantías × Días_Laborados × 0.12) / 360

PRIMA DE SERVICIOS (PS):
  PS = (Salario_Base_Mensual × Días_del_Semestre) / 360

VACACIONES EN DINERO (V):
  V = (Salario_Básico_Mensual × Días_Totales) / 720
  # Nota: divide entre 720 (= 360 × 2) porque corresponde a 15 días por cada año (360 días)
  # El auxilio de transporte NO entra en esta base
```

---

## [ESCENARIO_A]

### Empleador con cortes anuales al día (liquidación al 13 jun 2026)

> **Condición previa:** Cesantías 2025 consignadas en fondo antes del 15 feb 2026. Intereses pagados antes del 31 ene 2026. Prima 2025 pagada en dic 2025.

```yaml
escenario_A:
  descripcion: "Solo se pagan saldos causados en 2026 + vacaciones totales"
  
  prima_servicios_2026:
    base_cop: 2_000_000
    dias: 163  # 1 ene al 13 jun 2026
    formula: "(2_000_000 × 163) / 360"
    resultado_cop: 905_556

  cesantias_2026:
    base_cop: 2_000_000
    dias: 163
    formula: "(2_000_000 × 163) / 360"
    resultado_cop: 905_556

  intereses_cesantias_2026:
    cesantias_base_cop: 905_556
    dias: 163
    formula: "(905_556 × 163 × 0.12) / 360"
    resultado_cop: 49_202

  vacaciones_total:
    base_cop: 1_750_905  # solo salario básico — SIN auxilio de transporte
    dias_totales: 208
    formula: "(1_750_905 × 208) / 720"
    resultado_cop: 505_817

  total_liquidacion_cop: 2_366_131
```

---

## [ESCENARIO_B]

### Empleador acumulativo — sin cortes anuales (liquidación al 13 jun 2026)

> **Condición:** Las cesantías de 2025 NO fueron consignadas antes del 15 feb 2026. Aplica retroactividad por salario fijo.

```yaml
escenario_B:
  descripcion: "Deuda 2025 + 2026 — cesantías 2025 recalculadas con base 2026"
  principio_retroactividad: "Salario fijo no variado → base 2026 ($2.000.000) aplica a TODOS los días"

  prima_servicios_2025:
    base_cop: 1_623_500  # base vigente en 2025
    dias: 45
    formula: "(1_623_500 × 45) / 360"
    resultado_cop: 202_938
    nota: "Se liquida sobre base de su semestre de causación — NO retroactiva"

  prima_servicios_2026:
    base_cop: 2_000_000
    dias: 163
    formula: "(2_000_000 × 163) / 360"
    resultado_cop: 905_556

  cesantias_acumuladas_total:
    base_cop: 2_000_000  # actualización retroactiva — base 2026 para TODO el período
    dias_totales: 208
    formula: "(2_000_000 × 208) / 360"
    resultado_cop: 1_155_556

  intereses_cesantias_total:
    base_cesantias_cop: 1_155_556
    dias_totales: 208
    formula: "(1_155_556 × 208 × 0.12) / 360"
    resultado_cop: 80_052

  vacaciones_total:
    base_cop: 1_750_905  # solo salario básico
    dias_totales: 208
    formula: "(1_750_905 × 208) / 720"
    resultado_cop: 505_817

  total_liquidacion_cop: 2_849_919
```

---

## [TABLA_ESCENARIOS]

| Concepto Prestacional | Escenario A (Cortes al día) | Escenario B (Acumulativo) |
|---|---|---|
| Prima Servicios 2025 | *Pagada dic 2025 — no suma* | $202.938 COP |
| Prima Servicios 2026 | $905.556 COP | $905.556 COP |
| Cesantías 2025 | *Consignadas en fondo feb 2026* | *Retroactivas — integradas en total 2026* |
| Cesantías 2026 / Total | $905.556 COP | $1.155.556 COP (base actualizada) |
| Intereses Cesantías 2025 | *Pagados ene 2026* | $14.049 COP (proporción histórica) |
| Intereses Cesantías 2026 / Total | $49.202 COP | $80.052 COP |
| Vacaciones (208 días) | $505.817 COP | $505.817 COP |
| **TOTAL LIQUIDACIÓN** | **$2.366.131 COP** | **$2.849.919 COP** |
| **Sobrecosto por omisión** | — | **+$483.788 COP** |

---

## [ALERTAS_RIESGO]

### Prioridades explícitas del documento (ordenadas por impacto)

```yaml
alertas:
  - id: "ALERTA_01"
    prioridad: CRÍTICA
    situacion: "No renovación de contrato fijo sin notificar 30 días antes"
    consecuencia: "Prórroga automática por ministerio de ley → si se retira al trabajador = despido injustificado"
    sancion: "Indemnización Art. 64 = salarios de TODO el período de la nueva prórroga"
    tip_agente: "Verificar SIEMPRE si han transcurrido menos de 30 días antes del vencimiento"

  - id: "ALERTA_02"
    prioridad: CRÍTICA
    situacion: "Descuento en liquidación por renuncia intempestiva del trabajador"
    consecuencia: "ILEGAL desde 2002, ratificado por Ley 2466/2025"
    sancion: "Sanción moratoria Art. 65 CST: 1 día de salario por cada día de retraso"
    tip_agente: "Bloquear cualquier flujo que intente descontar días por preaviso no cumplido por trabajador"

  - id: "ALERTA_03"
    prioridad: ALTA
    situacion: "Cesantías no consignadas antes del 15 de febrero de cada año"
    consecuencia: "Retroactividad: base de cálculo sube al salario vigente del año de retiro"
    sobrecosto_ejemplo: "+$483.788 COP en período 208 días (caso de referencia)"
    tip_agente: "Verificar fecha de último depósito en fondo antes de calcular escenario"

  - id: "ALERTA_04"
    prioridad: ALTA
    situacion: "Aplicar Proyecto de Ley 504/2025 como norma vigente"
    consecuencia: "Error jurídico — esa ley NO está sancionada"
    tip_agente: "Usar siempre CST + Ley 2466/2025 como marco de referencia"

  - id: "ALERTA_05"
    prioridad: MEDIA
    situacion: "Incluir auxilio de transporte en base de vacaciones"
    consecuencia: "Cálculo incorrecto — el auxilio se excluye de vacaciones"
    tip_agente: "Para vacaciones: usar solo SMMLV. Para cesantías/prima: usar SMMLV + auxilio (si ≤ 2 SMMLV)"
```

---

## [PLANTILLAS]

### Plantilla 1 — Notificación de no renovación de contrato a término fijo

```
NOTIFICACIÓN DE NO RENOVACIÓN DE CONTRATO A TÉRMINO FIJO

Ciudad y fecha: {{CIUDAD}}, {{FECHA_NOTIFICACION}}

Señor(a): {{NOMBRE_TRABAJADOR}}
Cargo: {{CARGO}}
Finca: {{NOMBRE_FINCA}}

Estimado(a) señor(a):

Por medio de la presente, y de conformidad con el artículo 46 del Código Sustantivo del 
Trabajo modificado por la Ley 2466 de 2025, le comunicamos que el empleador {{NOMBRE_EMPLEADOR}} 
ha tomado la decisión de NO RENOVAR el contrato de trabajo a término fijo suscrito el 
{{FECHA_INICIO_CONTRATO}}, cuyo vencimiento opera el día {{FECHA_VENCIMIENTO}}.

Esta notificación se efectúa con {{DIAS_ANTICIPACION}} días calendario de anticipación, 
cumpliendo el mínimo legal de treinta (30) días.

Atentamente,
{{NOMBRE_EMPLEADOR}}
C.C. {{CEDULA_EMPLEADOR}}
NIT Finca/Empresa: {{NIT}}

CONSTANCIA DE RECIBO:
Nombre trabajador: ___________________________
Firma: ___________________________
Fecha de recibo: ___________________________
```

### Plantilla 2 — Esquema de liquidación final (JSON completable)

```json
{
  "liquidacion": {
    "trabajador": {
      "nombre": "{{NOMBRE}}",
      "cedula": "{{CEDULA}}",
      "cargo": "{{CARGO}}",
      "fecha_inicio": "{{FECHA_INICIO}}",
      "fecha_fin": "{{FECHA_FIN}}",
      "dias_totales": "{{DIAS_TOTALES}}",
      "salario_basico_mensual": "{{SALARIO_COP}}",
      "auxilio_transporte": "{{AUXILIO_COP}}",
      "base_prestacional": "{{BASE_COP}}"
    },
    "escenario": "{{A_o_B}}",
    "conceptos": {
      "prima_servicios_2025": {
        "aplica": "{{true/false}}",
        "valor_cop": "{{VALOR}}"
      },
      "prima_servicios_2026": {
        "dias": "{{DIAS}}",
        "valor_cop": "{{VALOR}}"
      },
      "cesantias": {
        "dias": "{{DIAS}}",
        "base_retroactiva": "{{true/false}}",
        "valor_cop": "{{VALOR}}"
      },
      "intereses_cesantias": {
        "dias": "{{DIAS}}",
        "valor_cop": "{{VALOR}}"
      },
      "vacaciones": {
        "dias_totales": "{{DIAS}}",
        "base_calculo_cop": "{{SOLO_SALARIO_SIN_AUXILIO}}",
        "valor_cop": "{{VALOR}}"
      },
      "indemnizacion": {
        "aplica": "{{true/false}}",
        "tipo": "{{despido_sin_justa_causa / prorroga_automatica}}",
        "valor_cop": "{{VALOR}}"
      }
    },
    "total_a_pagar_cop": "{{TOTAL}}",
    "plazo_pago_dias_habiles": 5
  }
}
```

### Plantilla 3 — Árbol de decisión de preaviso (pseudo-código para agente)

```python
def evaluar_preaviso(tipo_contrato, actor, dias_anticipacion, justa_causa=False, causal=None):
    """
    Retorna: accion_requerida, mecanismo_pago, riesgo_legal
    """
    if tipo_contrato == "OBRA_LABOR":
        return "TERMINACION_NATURAL", "SOLO_PRESTACIONES", "BAJO"
    
    if tipo_contrato == "TERMINO_FIJO":
        if actor == "EMPLEADOR":
            if dias_anticipacion >= 30:
                return "PREAVISO_EN_TIEMPO", "SALARIO_ORDINARIO_30_DIAS", "BAJO"
            elif dias_anticipacion > 0:
                return "PRORROGA_AUTOMATICA_ACTIVA", "INDEMNIZACION_ART64_PRORROGA", "CRITICO"
            else:  # vencimiento ya pasó o no notificó
                return "PRORROGA_AUTOMATICA_ACTIVA", "INDEMNIZACION_ART64_PRORROGA", "CRITICO"
        
        if actor == "TRABAJADOR":
            return "ACEPTAR_RENUNCIA", "LIQUIDACION_COMPLETA_SIN_DESCUENTOS", "BAJO"
    
    if tipo_contrato == "TERMINO_INDEFINIDO":
        if actor == "EMPLEADOR":
            if justa_causa:
                if causal in range(9, 16):  # causales 9 a 15
                    return "PREAVISO_15_DIAS", "PRESTACIONES_SIN_INDEMNIZACION", "BAJO"
                else:
                    return "TERMINACION_INMEDIATA", "PRESTACIONES_SIN_INDEMNIZACION", "BAJO"
            else:
                return "TERMINACION_INMEDIATA", "INDEMNIZACION_ART64 + PRESTACIONES", "MEDIO"
        
        if actor == "TRABAJADOR":
            return "ACEPTAR_RENUNCIA", "LIQUIDACION_COMPLETA_SIN_DESCUENTOS", "BAJO"
```

---

## [GLOSARIO]

| ID Término | Término | Definición técnica |
|---|---|---|
| `[G_PREAVISO]` | Preaviso | Manifestación unilateral de voluntad por la que una parte comunica a la otra la decisión de terminar el vínculo laboral en fecha futura. |
| `[G_PRORROGA_AUTO]` | Prórroga automática | Extensión del contrato a término fijo por un período igual al inicialmente pactado, que opera por ministerio de la ley cuando el empleador omite notificar la no renovación con ≥30 días de anticipación. |
| `[G_CLAUSULA_RESERVA]` | Cláusula de Reserva | Pacto contractual que faculta al empleador a rescindir el contrato de forma inmediata omitiendo el preaviso en tiempo, siempre que pague los salarios del período omitido. Fundamento: Art. 48 CST. |
| `[G_CESANTIAS]` | Cesantías | Prestación social equivalente a 1 mes de salario por cada año laborado, proporcional por fracción. Se deposita en fondo antes del 15 de febrero de cada año. |
| `[G_INTERESES_CES]` | Intereses sobre Cesantías | Rendimiento del 12% anual sobre el saldo de cesantías. Se paga directamente al trabajador antes del 31 de enero. |
| `[G_PRIMA]` | Prima de Servicios | Prestación social equivalente a 15 días de salario por cada semestre laborado. Se paga en junio y diciembre. |
| `[G_VACACIONES]` | Vacaciones | 15 días hábiles de descanso remunerado por cada año. Se compensan en dinero al terminar el contrato si no se disfrutaron. Base de cálculo: solo salario básico (sin auxilio de transporte). |
| `[G_RETROACTIVIDAD]` | Retroactividad de Cesantías | Principio por el cual, si las cesantías no son consignadas en el fondo oportunamente y el salario es fijo (aunque haya cambio de SMMLV entre años), la base de cálculo se actualiza al último salario devengado para todo el período. |
| `[G_SMMLV]` | SMMLV | Salario Mínimo Mensual Legal Vigente. 2025: $1.423.500 COP / 2026: $1.750.905 COP. |
| `[G_SANCION_MORATORIA]` | Sanción Moratoria | Multa del Art. 65 CST: 1 día de salario por cada día de retraso en el pago de la liquidación final tras la terminación del contrato. |
| `[G_BASE_PRESTACIONAL]` | Base Prestacional | Suma de SMMLV + Auxilio de Transporte/Conectividad usada para calcular cesantías y prima. 2025: $1.623.500 COP / 2026: $2.000.000 COP. Aplica solo para trabajadores que devenguen ≤ 2 SMMLV. |
| `[G_DESPIDO_SIN_CAUSA]` | Despido sin Justa Causa | Terminación unilateral del contrato por el empleador sin incurrir en ninguna de las causales del Art. 62 CST. Genera obligación de indemnización según Art. 64 CST. |
| `[G_JUSTA_CAUSA]` | Justa Causa | Causal taxativa del Art. 62 CST que faculta al empleador a terminar el contrato sin pagar indemnización. Las causales 9 a 15 exigen preaviso de 15 días. |
| `[G_CST]` | CST | Código Sustantivo del Trabajo — norma matriz del derecho laboral colombiano. |
| `[G_LEY_2466]` | Ley 2466/2025 | Reforma Laboral colombiana — modifica Arts. 46, 47, 48 del CST y consagra protección especial al campesinado. |

---

*Fin del documento · KB_Preaviso_Laboral_Fincas_Rurales.md*  
*Optimizado para consumo por agente de IA — junio 2026*
