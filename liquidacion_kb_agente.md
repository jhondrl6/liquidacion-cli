# KNOWLEDGE BASE — LIQUIDACIÓN PERIÓDICA DE PRESTACIONES SOCIALES
> Optimizado para consumo por agente de IA. Versión: 1.0 | Fuente: `liquidacion_20251202_204225.pdf`

---

## [INDICE_RAPIDO]

| Para saber sobre... | Ir a sección |
|---|---|
| Identidad del empleador / trabajador | `[PARTES]` |
| Valores y montos de cada prestación | `[PRESTACIONES]` |
| Plazos legales de pago (deadlines críticos) | `[PLAZOS]` |
| Bases de cálculo y exclusiones | `[BASES_CALCULO]` |
| Variables para completar en scripts | `[SCHEMA_VARIABLES]` |
| Normativa legal aplicable | `[MARCO_LEGAL]` |
| Glosario de términos técnicos | `[GLOSARIO]` |
| Flujo de ejecución para scripts | `[FLUJO_EJECUCION]` |
| Cláusulas especiales y notas | `[CLAUSULAS_ESPECIALES]` |

---

## [PARTES]

### Empleador

```yaml
empleador:
  nombre: "HILDALIRIA RAIGOZA LOAIZA"
  cedula: "42.066.783"
  rol: "EMPLEADOR / FIRMANTE"
```

### Trabajador

```yaml
trabajador:
  nombre: "PEDRO LUIS FRANCO"
  cedula: "7.247.867"
  tipo_contrato: "indefinido"
  reside_lugar_trabajo: true
  lugar_trabajo: "Finca Rural"
```

---

## [PERIODO]

```yaml
periodo_liquidado:
  fecha_inicio: "2024-11-16"
  fecha_fin: "2025-11-15"
  dias_totales: 365
  modo: "PERIODICA"
  fecha_generacion_documento: "2025-12-02"
  pais: "Colombia"
  anno: 2025
```

---

## [PRESTACIONES]

Tabla maestra de todas las prestaciones liquidadas:

| ID | Concepto | Valor (COP) | Días Base | Plazo de Pago | Base Legal |
|---|---|---|---|---|---|
| `PREST_001` | Cesantías | $1.500.000 | 365 | 2026-02-14 | Art. 249-250 CST |
| `PREST_002` | Intereses sobre Cesantías | $180.000 | 365 | 2026-01-31 | Ley 50/1990 Art. 99 |
| `PREST_003` | Prima de Servicios | $575.000 | 138 | 2025-12-20 | Art. 306-308 CST |
| `PREST_004` | Compensación Vacaciones | $375.000 | 7.5 | N/A (ya pagado) | Art. 189 CST |
| **TOTAL** | — | **$2.630.000** | — | — | — |

### Detalle en JSON (schema listo para script)

```json
{
  "liquidacion": {
    "id": "LIQ-20251202-PEDRO",
    "modo": "PERIODICA",
    "periodo": {
      "inicio": "2024-11-16",
      "fin": "2025-11-15",
      "dias": 365
    },
    "prestaciones": [
      {
        "id": "PREST_001",
        "concepto": "Cesantias",
        "valor_cop": 1500000,
        "dias": 365,
        "plazo_pago": "2026-02-14",
        "base_legal": "Art. 249-250 CST",
        "prioridad_pago": 2
      },
      {
        "id": "PREST_002",
        "concepto": "Intereses_Cesantias",
        "valor_cop": 180000,
        "dias": 365,
        "plazo_pago": "2026-01-31",
        "base_legal": "Ley 50/1990 Art. 99",
        "prioridad_pago": 1
      },
      {
        "id": "PREST_003",
        "concepto": "Prima_Servicios",
        "valor_cop": 575000,
        "dias": 138,
        "plazo_pago": "2025-12-20",
        "base_legal": "Art. 306-308 CST",
        "prioridad_pago": 0
      },
      {
        "id": "PREST_004",
        "concepto": "Compensacion_Vacaciones",
        "valor_cop": 375000,
        "dias": 7.5,
        "plazo_pago": null,
        "base_legal": "Art. 189 CST",
        "prioridad_pago": null,
        "nota": "Ya pagado por acuerdo mutuo. No genera deadline adicional."
      }
    ],
    "total_cop": 2630000
  }
}
```

---

## [PLAZOS]

> ⚠️ **PRIORIDADES EXPLÍCITAS** — ordenadas por urgencia (menor fecha = mayor prioridad):

```yaml
plazos_pago_ordenados:
  - prioridad: 0          # MÁS URGENTE
    concepto: "Prima de Servicios"
    deadline: "2025-12-20"
    dias_restantes_desde_generacion: 18
    valor_cop: 575000
    base_legal: "Art. 306-308 CST"

  - prioridad: 1
    concepto: "Intereses sobre Cesantías"
    deadline: "2026-01-31"
    valor_cop: 180000
    base_legal: "Ley 50/1990 Art. 99"

  - prioridad: 2          # MENOS URGENTE
    concepto: "Cesantías"
    deadline: "2026-02-14"
    valor_cop: 1500000
    base_legal: "Art. 249-250 CST"
    destino: "Fondo de Cesantías (no pago directo al trabajador en liquidación periódica)"

  - prioridad: null
    concepto: "Compensación Vacaciones"
    deadline: null
    nota: "Pagado en esta liquidación. Sin deadline futuro."
```

---

## [BASES_CALCULO]

### Exclusiones aplicadas (críticas para reproducir el cálculo)

```yaml
exclusiones:
  - concepto: "Valor excluido por residencia en lugar de trabajo"
    monto_cop: 200000
    razon: "Trabajador reside en Finca Rural — excluido del SBL"
    aplica_a: ["Cesantias", "Intereses_Cesantias", "Prima_Servicios"]

  - concepto: "Horas extras, recargos y auxilios"
    monto_cop: null   # no especificado en documento
    razon: "Excluidos del SBL para cálculo de vacaciones"
    aplica_a: ["Compensacion_Vacaciones"]
```

### Fórmulas implícitas

```python
# Cesantías (Art. 249 CST)
# cesantias = (SBL * dias_trabajados) / 360
# SBL base = salario_mensual - exclusion_residencia (200.000 COP)

# Intereses sobre Cesantías (Ley 50/1990)
# intereses = cesantias * 0.12  =>  1.500.000 * 0.12 = 180.000 ✓

# Prima de Servicios (Art. 306 CST)
# prima = (SBL * dias_periodo_prima) / 360
# Nota: días usados = 138 (no 365), indica semestre parcial o período específico

# Compensación Vacaciones (Art. 189 CST)
# comp_vac = (SBL_vac * dias_compensados) / 30
# dias_compensados = 7.5
```

---

## [CLAUSULAS_ESPECIALES]

```yaml
clausulas:
  - id: "CLAUSULA_VAC_189"
    tipo: "Acuerdo mutuo compensación vacaciones"
    base_legal: "Art. 189 CST"
    descripcion: >
      El trabajador solicitó y el empleador aceptó compensar en dinero 
      7.5 días de vacaciones. El trabajador declara haberlos recibido 
      en esta liquidación ($375.000) y se compromete a disfrutar los 
      días restantes antes de causar nuevo período.
    firmado_por: ["PEDRO LUIS FRANCO", "Hildaliria Raigoza L."]
    estado: "EJECUTADO — incluido en total liquidación"

  - id: "NOTA_RESIDENCIA"
    tipo: "Exclusión SBL por beneficio en especie"
    descripcion: >
      El trabajador reside en la Finca Rural (lugar de trabajo). 
      El valor de este beneficio ($200.000) se excluye del 
      Salario Base de Liquidación conforme a la normativa.
    impacto: "Reduce SBL en $200.000 COP para todos los conceptos aplicables"
```

---

## [SCHEMA_VARIABLES]

Plantilla YAML lista para completar al procesar una nueva liquidación:

```yaml
# TEMPLATE: liquidacion_periodica_colombia.yaml
# Completar todas las variables marcadas con <VALOR>

trabajador:
  nombre: "<NOMBRE_COMPLETO>"
  cedula: "<CC>"
  tipo_contrato: "<indefinido|fijo|obra_labor>"
  reside_lugar_trabajo: <true|false>
  lugar_trabajo: "<DESCRIPCION>"

empleador:
  nombre: "<NOMBRE_COMPLETO>"
  cedula: "<CC>"

periodo:
  inicio: "<YYYY-MM-DD>"
  fin: "<YYYY-MM-DD>"
  dias_totales: <N>

salario_base_liquidacion:
  salario_mensual: <VALOR_COP>
  exclusion_residencia: <VALOR_COP_O_0>
  exclusion_extras_recargos: <VALOR_COP_O_0>
  sbl_efectivo: <RESULTADO>

prestaciones:
  cesantias:
    calcular: true
    dias: <N>
    plazo_consignacion: "<YYYY-02-14>"  # siempre 14 feb año siguiente
  intereses_cesantias:
    calcular: true
    tasa: 0.12
    plazo_pago: "<YYYY-01-31>"          # siempre 31 ene año siguiente
  prima_servicios:
    calcular: true
    dias_periodo: <N>
    plazo_pago: "<YYYY-MM-DD>"
  compensacion_vacaciones:
    aplicar: <true|false>
    dias_compensar: <N_MAX_15>
    acuerdo_mutuo: <true|false>

exclusiones_aplicadas:
  - descripcion: "<RAZON>"
    monto: <VALOR_COP>
```

---

## [MARCO_LEGAL]

```yaml
normas_referenciadas:
  - id: "LEY_CST_249_250"
    nombre: "Código Sustantivo del Trabajo — Art. 249-250"
    aplica_a: "Cesantías"
    obligacion: "Consignar al fondo de cesantías antes del 14 de febrero"

  - id: "LEY_50_1990_ART99"
    nombre: "Ley 50 de 1990 — Art. 99"
    aplica_a: "Intereses sobre Cesantías"
    obligacion: "Pagar directamente al trabajador antes del 31 de enero"
    tasa_anual: "12%"

  - id: "LEY_CST_306_308"
    nombre: "Código Sustantivo del Trabajo — Art. 306-308"
    aplica_a: "Prima de Servicios"
    obligacion: "Pagar en junio y diciembre de cada año"

  - id: "LEY_CST_189"
    nombre: "Código Sustantivo del Trabajo — Art. 189"
    aplica_a: "Compensación de Vacaciones en dinero"
    restriccion: "Máximo 15 días compensables por período. Requiere acuerdo mutuo."
```

---

## [FLUJO_EJECUCION]

Arquitectura de scripts recomendada para ejecutar esta liquidación:

```
┌─────────────────────────────────────────────────────────┐
│                  FLUJO DE EJECUCIÓN                     │
│              Liquidación Periódica CST                  │
└─────────────────────────────────────────────────────────┘

PASO 0 — Ingesta de datos
  └─► Leer schema [SCHEMA_VARIABLES] y poblar variables
  └─► Validar: fechas, cédulas, tipo contrato, SBL

PASO 1 — Calcular SBL efectivo
  └─► SBL = salario_mensual - exclusion_residencia - exclusion_extras
  └─► Validar contra SMMLV (no puede ser inferior)

PASO 2 — Calcular prestaciones (orden de dependencia)
  ├─► [2a] Cesantías         → requiere: SBL, días período
  ├─► [2b] Intereses         → requiere: resultado cesantías (2a)
  ├─► [2c] Prima             → requiere: SBL, días período prima
  └─► [2d] Comp. Vacaciones  → requiere: SBL_vacaciones (sin extras), acuerdo_mutuo=true

PASO 3 — Asignar plazos legales
  └─► Mapear cada prestación a su deadline (ver [PLAZOS])

PASO 4 — Generar documento
  └─► Poblar plantilla con resultados
  └─► Incluir cláusula Art. 189 si comp_vacaciones.aplicar = true
  └─► Requerir firmas: trabajador + empleador

PASO 5 — Validación final
  └─► Total calculado == suma de prestaciones individuales
  └─► Todos los plazos son fechas futuras respecto a fecha_generacion
  └─► Exclusiones documentadas y justificadas
```

```yaml
dependencias_entre_scripts:
  script_cesantias:
    inputs: ["sbl_efectivo", "dias_periodo"]
    outputs: ["valor_cesantias"]

  script_intereses:
    inputs: ["valor_cesantias"]   # depende de script_cesantias
    outputs: ["valor_intereses"]

  script_prima:
    inputs: ["sbl_efectivo", "dias_periodo_prima"]
    outputs: ["valor_prima"]

  script_vacaciones:
    inputs: ["sbl_vacaciones", "dias_compensar", "acuerdo_mutuo"]
    outputs: ["valor_compensacion_vac"]

  script_total:
    inputs: ["valor_cesantias", "valor_intereses", "valor_prima", "valor_compensacion_vac"]
    outputs: ["total_liquidacion", "documento_final"]
```

---

## [GLOSARIO]

| ID Término | Término | Definición técnica |
|---|---|---|
| `TERM_CST` | CST | Código Sustantivo del Trabajo — marco legal laboral colombiano |
| `TERM_SBL` | SBL | Salario Base de Liquidación — monto sobre el cual se calculan las prestaciones, puede diferir del salario nominal por exclusiones |
| `TERM_SMMLV` | SMMLV | Salario Mínimo Mensual Legal Vigente — piso legal del salario en Colombia |
| `TERM_CESANTIAS` | Cesantías | Prestación equivalente a 1 mes de salario por año trabajado; se consigna a un fondo, no al trabajador directamente |
| `TERM_INTERESES` | Intereses s/ Cesantías | 12% anual sobre el saldo de cesantías; se paga directamente al trabajador |
| `TERM_PRIMA` | Prima de Servicios | Equivalente a 15 días de salario por semestre trabajado; pagada en junio y diciembre |
| `TERM_VAC` | Vacaciones | 15 días hábiles de descanso por año; hasta 15 días pueden compensarse en dinero por acuerdo |
| `TERM_COMP_VAC` | Compensación de Vacaciones | Pago en dinero de días de vacaciones no disfrutados, requiere acuerdo mutuo, máx. 15 días |
| `TERM_LIQUIDACION_PERIODICA` | Liquidación Periódica | Liquidación que ocurre mientras la relación laboral está vigente (vs. liquidación definitiva al terminar contrato) |
| `TERM_EXCLUSION_RESIDENCIA` | Exclusión por Residencia | Valor del alojamiento provisto por el empleador, excluido del SBL cuando el trabajador reside en el lugar de trabajo |
| `TERM_FONDO_CESANTIAS` | Fondo de Cesantías | Entidad financiera administradora de las cesantías; el empleador consigna, no paga directamente al trabajador |

---

## [DOCUMENTO_FUENTE]

```yaml
metadata_pdf:
  nombre_archivo: "liquidacion_20251202_204225.pdf"
  fecha_generacion: "2025-12-02T20:42:25"
  paginas: 2
  firmantes_requeridos:
    - rol: "Trabajador"
      nombre: "PEDRO LUIS FRANCO"
    - rol: "Empleador"
      nombre: "Hildaliria Raigoza L."
      cedula: "42.066.783"
  estado_firmas: "PENDIENTE — documento generado, firmas no confirmadas en PDF"
```
