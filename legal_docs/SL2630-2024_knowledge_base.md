# BASE DE CONOCIMIENTO: SL2630-2024
## Sentencia Corte Suprema de Justicia — Sala de Casación Laboral
**Radicación:** 101342 | **Acta:** 34 | **Fecha:** 2024-09-17
**Magistrado Ponente:** Martín Emilio Beltrán Quintero
**Firmantes adicionales:** Olga Yineth Merchán Calderón · Marirraquel Rodelo Navarro

---

## ÍNDICE RÁPIDO

| Para… | Ir a sección |
|---|---|
| Identificar partes del proceso | [PARTES] |
| Entender qué se reclamó | [PRETENSIONES] |
| Saber qué periodos están prescritos | [PRESCRIPCION] |
| Calcular cesantías adeudadas | [LIQUIDACION_CESANTIAS] |
| Calcular vacaciones adeudadas | [LIQUIDACION_VACACIONES] |
| Calcular intereses sobre cesantías | [LIQUIDACION_INTERESES_CESANTIAS] |
| Obtener el historial salarial año a año | [HISTORIAL_SALARIAL] |
| Entender la regla sobre salario base de liquidación | [REGLAS_SALARIO_BASE] |
| Entender cuándo opera la excepción de compensación | [EXCEPCION_COMPENSACION] |
| Conocer el marco legal de CTAs aplicable | [MARCO_LEGAL_CTA] |
| Entender los criterios de intermediación laboral ilegal | [INDICIOS_INTERMEDIACION] |
| Mapping a schemas Pydantic del motor | [MAPPING_PYDANTIC] |
| Resultado final del fallo (montos condenados) | [DECISION_FINAL] |
| Glosario de términos | [GLOSARIO] |

---

## [PARTES]

```yaml
demandante:
  nombre: "Juan Enrique Moreno Palma"
  rol_procesal: "Accionante / Recurrente en casación"

demandadas:
  - id: AVIANCA
    nombre_completo: "Aerovías del Continente Americano S.A. — AVIANCA S.A."
    rol: "Empleadora real (contrato realidad)"
    condena: true

  - id: SERVICOPAVA
    nombre_completo: "Cooperativa de Trabajo Asociado — Servicopava (en liquidación)"
    rol: "Intermediaria laboral ilegal / Simple intermediaria"
    condena: "solidaria con AVIANCA"

otros_actores_iniciales:
  - nombre: "Jair Bernal Ariza"
    estado: "Concilió en audiencia del 2022-10-10 — proceso terminado respecto de él"
  - nombre: "Robinsson Barreto Pinzón"
    estado: "Concilió en audiencia del 2022-10-10 — proceso terminado respecto de él"
```

---

## [PERIODO_LABORAL]

```yaml
vinculo_laboral_reconocido:
  inicio: "2006-09-01"
  fin: "2017-10-31"
  duracion_anios: 11.17
  tipo_contrato: "A término indefinido (contrato realidad)"
  modalidad_formal_previa: "Convenio de asociación CTA Servicopava"

vinculo_previo_no_reclamado:
  inicio: "2006-05-01"   # Misión Temporal Ltda.
  fin: "2006-08-31"      # No hace parte de la condena
  nota: "Periodo con empresa temporal diferente; no integra la relación laboral declarada"

cargos_desempeñados:
  - "Auxiliar de asistencia en tierra"
  - "Auxiliar de conductor"
  - "Líder de asistencia en tierra"
  - "Líder de operaciones terrestres"   # último cargo

ultimo_cargo_descripcion: >
  Gestionar la coordinación en cuanto a recursos humanos y equipos
  en tierra para la atención oportuna de los vuelos en BOG.
```

---

## [PRETENSIONES]

Prestaciones reclamadas (base de la demanda):

| # | Concepto | Resultado en fallo CSJ |
|---|---|---|
| 1 | Auxilio de cesantías | **RECONOCIDO** (monto modificado) |
| 2 | Intereses sobre cesantías | **RECONOCIDO** (periodo no prescrito) |
| 3 | Prima de servicios | Prescrita para periodos anteriores al 06-07-2017; **pagada** para periodo no prescrito |
| 4 | Vacaciones | **RECONOCIDA diferencia** ($39.367) |
| 5 | Dotación calzado y vestido | Prescrita / absueltas |
| 6 | Sanción no consignación cesantías (Ley 50/90) | No objeto de apelación → no se pronuncia CSJ |
| 7 | Indemnización por terminación sin justa causa | **NO procede** (vínculo continuó en SAI) |
| 8 | Indemnización moratoria (art. 65 CST) | No objeto de apelación → no se pronuncia CSJ |
| 9 | Costas | Primer grado a cargo demandadas; alzada: no causadas |

---

## [PRESCRIPCION]

### Regla general aplicada

```
Normas: Art. 488 CST + Art. 151 CPTSS
Plazo: 3 años desde exigibilidad de cada derecho
Interrupción: presentación de demanda (una sola vez)
Reinicio: desde la interrupción corre nuevo trienio
```

### Cronología del caso

```yaml
fecha_terminacion_vinculo: "2017-10-31"
fecha_presentacion_demanda: "2020-07-06"   # folio 2, cuaderno 2024033744398
fecha_corte_prescripcion: "2017-07-06"     # 3 años antes de la demanda

derechos_PRESCRITOS:
  descripcion: "Todos los causados antes del 2017-07-06"
  excepciones:
    - concepto: "Auxilio de cesantías"
      regla: >
        Prescripción se contabiliza desde la terminación de la relación laboral
        (no desde cada anualidad causada). Por tanto, NO prescrito.
    - concepto: "Vacaciones"
      regla: >
        Se exigen un año después de causadas; período no prescrito
        abarca desde el 06-07-2016 en adelante.

derechos_NO_PRESCRITOS:
  - "Cesantías (todas las anualidades por regla especial de terminación)"
  - "Intereses sobre cesantías del 06-07-2017 al 31-10-2017"
  - "Vacaciones causadas a partir del 06-07-2016"
  - "Prima de servicios causada a partir del 06-07-2017"
```

> **NOTA para motor:** La constante `_PRESCRIPCION_ANIOS = 3` en `engine.py` deriva de Art. 488 CST, **no** del texto de esta sentencia. La sentencia confirma esa constante pero no la redefine.

---

## [HISTORIAL_SALARIAL]

Fuente: Folios 173–178 (histórico de sumas recibidas 2006–2010) y planillas de seguridad social (folios 145–146 y 148–184, cuaderno 2024034240689).

### Tabla principal — Salario promedio anual acreditado

| Año | Salario Promedio | Folio(s) fuente | Días computados |
|-----|-----------------|-----------------|-----------------|
| 2006 | $997.095 | 173 | 120 (sept–dic) |
| 2007 | $763.716 | 174 | 360 |
| 2008 | $1.379.251 | 175 | 360 |
| 2009 | $1.929.316 | 176 | 360 |
| 2010 | $2.020.339 | 178 | 360 |
| 2011 | $1.983.333 | 169–172 | 360 |
| 2012 | $2.200.417 | 165–168 | 360 |
| 2013 | $2.274.667 | 161–164 | 360 |
| 2014 | $2.352.500 | 157–160 | 360 |
| 2015 | $2.663.583 | 152–156 | 360 |
| 2016 | $2.686.666 | 148–152 | 360 |
| 2017 | $3.089.608 ¹ / $2.872.211 ² | 145–146, 184 | — |

**Notas:**
- ¹ Salario base usado para prima de servicios (auxilio semestral)
- ² Salario base usado para vacaciones (art. 189 CST num. 3 → último salario devengado = valor en planilla seguridad social)

### Mapping a Schema Pydantic `Salario.sbl_por_anio`

```python
# dict[int, Decimal]
sbl_por_anio = {
    2006: Decimal("997095"),
    2007: Decimal("763716"),
    2008: Decimal("1379251"),
    2009: Decimal("1929316"),
    2010: Decimal("2020339"),
    2011: Decimal("1983333"),
    2012: Decimal("2200417"),
    2013: Decimal("2274667"),
    2014: Decimal("2352500"),
    2015: Decimal("2663583"),
    2016: Decimal("2686666"),
    # 2017 bifurcado: usar 3089608 para prima, 2872211 para vacaciones
}
```

---

## [REGLAS_SALARIO_BASE]

### Por concepto

```yaml
cesantias:
  norma: "Art. 253 CST + ordinal 7 Art. 99 Ley 50/1990"
  regla: >
    Último salario mensual devengado si no hubo variación en últimos 3 meses.
    En caso de salarios variables: promedio del último año (o tiempo servido si < 1 año).
  fuente_jurisprudencial: "CSJ SL, 27 jul 2001, rad. 16074"
  aplicacion_en_caso: >
    Se usó el salario promedio de cada año según histórico de sumas recibidas
    reportadas a seguridad social.

vacaciones_compensadas_en_dinero:
  norma: "Art. 189 CST num. 3 + D.L. 2351/1965 art. 14"
  regla: >
    Base = ÚLTIMO salario devengado por el trabajador (no promedio).
  valor_aplicado: 2872211   # COP — planilla seguridad social folio 145
  fuente_jurisprudencial: "CSJ SL, 6 oct 2006, rad. 28718"
  nota: >
    El fallo corrigió el cálculo de la CTA que usó $2.804.257 (promedio);
    la CSJ aplicó $2.872.211 (último salario en planilla SS).

prima_de_servicios:
  norma: "Auxilio semestral equivalente"
  valor_aplicado: 3089608   # COP — IBC folio 145–146
  periodo: "2017-07-01 al 2017-10-31 (4 meses = 10 días proporción semestral)"
```

---

## [LIQUIDACION_CESANTIAS]

### Resultado final CSJ

| Año | Salario base | Días | Valor cesantía anual |
|-----|-------------|------|----------------------|
| 2006 | $997.095 | 120 | **$332.335** |
| 2007 | $763.716 | 360 | **$763.716** |
| 2008 | $1.379.251 | 360 | **$1.379.251** |
| 2009 | $1.929.316 | 360 | **$1.929.316** |
| 2010 | $2.020.339 | 360 | **$2.020.339** |
| 2011 | $1.983.333 | 360 | **$2.062.695** |
| 2012 | $2.200.417 | 360 | **$2.200.417** |
| 2013 | $2.274.667 | 360 | **$2.274.667** |
| 2014 | $2.352.500 | 360 | **$2.352.500** |
| 2015 | $2.663.583 | 360 | **$2.663.583** |
| 2016 | $2.686.666 | 360 | **$2.686.666** |
| **TOTAL ADEUDADO** | | | **$20.665.485** |

**Ya pagado (periodo 31-12-2016 a 31-10-2017):**
- Causado: $2.418.475
- Pagado previamente: $1.388.606
- Sufragado en liquidación CTA: $1.029.869
- Saldo este periodo: $0 (cubierto por compensación)

**Monto condenado por CSJ (auxilio cesantías):** `$20.665.485`
*(Modifica el fallo de primera instancia que reconoció solo $16.193.804)*

### Fórmula aplicada

```
cesantia_anio = (salario_promedio * dias) / 360
```

> Para 2006 (120 días): $997.095 × 120 / 360 = **$332.335**
> Para años completos: salario_promedio × 1 = **salario_promedio** (cuando días = 360)

---

## [LIQUIDACION_VACACIONES]

```yaml
periodo_no_prescrito_analizado: "2016-09-01 al 2017-10-31"
  # (14 meses según CTA; compensadas en dinero)

salario_base_correcto: 2872211     # COP — último salario devengado (planilla SS)
salario_base_incorrecto_CTA: 2804257  # COP — promedio usado por CTA (erróneo)

dias_a_cancelar: 17.38

valor_correcto:   1663967    # COP  → salario_base_correcto * (17.38/30)
valor_pagado_CTA: 1624600    # COP

diferencia_adeudada: 39367   # COP  → CONDENA ADICIONAL CSJ

nota_2016: >
  A folio 182 cuaderno 2024034240689 consta que en 2016 recibió
  la compensación por descanso; por tanto el período no prescrito
  comienza el 06-07-2016 pero ese año ya fue pagado.
```

**Monto condenado por CSJ (vacaciones):** `$39.367`

---

## [LIQUIDACION_INTERESES_CESANTIAS]

```yaml
periodo_no_prescrito: "2017-07-06 al 2017-10-31"
base_calculo: 2418475      # COP — cesantía causada ese período
tasa_aplicada: 0.038       # 3.8%
valor_bruto: 91902         # COP  → 2418475 × 0.038
ya_pagado_CTA: 41195       # COP  (rendimiento auxilio anual en liquidación)
saldo_adeudado: 50707      # COP  → 91902 - 41195

formula: "intereses = base_cesantia_periodo * 0.038"
```

**Monto condenado por CSJ (intereses cesantías):** `$50.707`

---

## [DECISION_FINAL]

```yaml
sentencia_casada: "Tribunal Superior Bogotá, Sala Laboral — 2023-06-30"

resolucion_CSJ:
  primero:
    accion: "ADICIONAR fallo de primera instancia"
    condenas_adicionales:
      vacaciones: 39367        # COP
      intereses_cesantias: 50707  # COP

  segundo:
    accion: "MODIFICAR numeral tercero primera instancia"
    concepto: "Auxilio de cesantías"
    valor_anterior: 16193804   # COP (primera instancia)
    valor_correcto: 20665485   # COP (CSJ)

  tercero:
    accion: "CONFIRMAR en lo demás"

  cuarto:
    costas_primera_instancia: "A cargo de demandadas (como lo dijo a quo)"
    costas_alzada: "No se imponen (no causadas)"

responsabilidad:
  principal: "AVIANCA S.A."
  solidaria: "Cooperativa de Trabajo Asociado Servicopava — En Liquidación"

resumen_montos_COP:
  cesantias:              20665485
  vacaciones_diferencia:     39367
  intereses_cesantias:       50707
  prima_servicios:        "Pagada (no genera condena adicional)"
  total_condena_nueva:    20755559   # cesantias + vacaciones_diferencia + intereses
```

---

## [EXCEPCION_COMPENSACION]

```yaml
excepcion_prospera: true
fundamento_jurisprudencial:
  - "CSJ SL5595-2019"
  - "CSJ SL2726-2022"
  - "CSJ SL3570-2020"
  - "CSJ SL1715-2024"

regla: >
  Los pagos recibidos como "compensaciones" en el marco del convenio
  de trabajo asociado se computan como contraprestación del mismo
  servicio personal prestado a AVIANCA S.A.
  No hay doble pago: se descuenta lo percibido como compensación
  de las prestaciones laborales causadas.

aplicacion_en_caso:
  - concepto: "Prima de servicios"
    compensado_con: "Auxilio semestral ($1.029.869)"
    resultado: "Saldo = $0 (pagada)"
  - concepto: "Vacaciones"
    compensado_con: "Descanso anual en dinero ($1.624.600)"
    diferencia_adeudada: 39367
  - concepto: "Cesantías 2016-2017"
    compensado_con: "Auxilio anual + rendimiento ($1.029.869 + $41.195 + $1.388.606 previo)"
    resultado: "Saldo = $0 para ese período"

advertencia_para_motor: >
  Al calcular sumas adeudadas, SIEMPRE aplicar excepción de compensación:
  descontar lo efectivamente pagado por la CTA bajo el régimen de
  compensaciones antes de determinar el saldo a favor del trabajador.
```

---

## [MARCO_LEGAL_CTA]

### Normas aplicables (en orden de jerarquía)

```yaml
normas:
  - id: LEY_79_1988
    articulo: 59
    contenido: >
      Régimen de trabajo, previsión, seguridad social y compensación se
      establece en estatutos y reglamentos propios (acuerdo cooperativo).
      No sujeto a legislación laboral de trabajadores dependientes.
    articulo_70: >
      CTA: aquellas que vinculan el trabajo personal de sus asociados
      para producción de bienes, obras o prestación de servicios.

  - id: DECRETO_4588_2006
    articulo_10: >
      El trabajo cooperativo se rige por sus propios estatutos;
      no le es aplicable la legislación laboral ordinaria.
    articulo_16: >
      Empleador = persona natural o jurídica que se beneficie con el trabajo.
    articulo_17:
      prohibicion: >
        Prohibición expresa para actuar como intermediario o empresa
        de servicios temporales.
      consecuencia: >
        CTA responderá solidariamente; condición de empleador recae
        en quien se beneficia del trabajo.

  - id: LEY_1233_2008
    articulo_7: >
      En ningún caso el contratante podrá intervenir directa o
      indirectamente en decisiones internas de la cooperativa,
      ni en selección de trabajadores, potestad reglamentaria
      ni disciplinaria.

  - id: LEY_1429_2010
    articulo_63: >
      Personal requerido para actividades misionales permanentes NO
      puede estar vinculado a través de CTAs que hagan intermediación
      laboral o bajo modalidad que afecte derechos constitucionales,
      legales y prestacionales.
    definicion_actividad_misional_permanente: >
      Actividades o funciones directamente relacionadas con la
      producción del bien o servicios característicos de la empresa.
    reglamentado_por: "Decreto 2025 de 2011, Art. 1"
```

---

## [INDICIOS_INTERMEDIACION]

La Corte (CSJ SL2084-2023) sistematizó los supuestos indicativos de intermediación laboral ilegal:

```yaml
indicios_intermediacion_ilegal:
  (i):
    descripcion: >
      Contratación en el marco de servicios y actividades misionales
      permanentes + empresa contratante ejerce subordinación jurídica
      sobre los trabajadores asociados.
    referencia: "CSJ SL5595-2019"

  (ii):
    descripcion: >
      CTA carece de estructura propia y especializada; no es autónoma
      en su gestión administrativa y financiera.
    referencia: "CSJ SL, 17 oct 2008, rad. 30605; SL665-2013; SL6441-2013; SL12707-2017; SL1430"

  (iii):
    descripcion: >
      Trabajador asociado se INTEGRA a la organización de la empresa
      (evidenciado por organigrama, manuales, subordinación continua).
    referencia: "CSJ SL3436-2021; Recomendación 198 OIT"

  adicional:
    descripcion: >
      Asociados NO son dueños de los medios de producción o laborales
      (elemento indicativo de vínculo asociado aparente).
    referencia: "CSJ SL3777-2022"
```

### Hechos del caso que acreditaron intermediación ilegal (Servicopava)

```yaml
hechos_probados:
  - "Actividad contratada = transporte aéreo (objeto social principal de AVIANCA)"
  - "CTA no tenía estructura funcional para prestar el servicio; dependía de elementos de AVIANCA"
  - "AVIANCA capacitó a los cooperados (certificados y cursos folio 579–583)"
  - "AVIANCA era propietaria de las herramientas e implementos de labor"
  - "Oferta mercantil obligaba a AVIANCA a entregar equipos en comodato"
  - "Actor participó en semillero de formación de AVIANCA antes de ingresar a la CTA"
  - "Actividades bajo continua supervisión y subordinación de AVIANCA"
  - "Actor integrado al organigrama de AVIANCA (folio 346 — Gerencia Operaciones Terrestres BOG)"
  - "Jefes directos pertenecían a AVIANCA (testigo Ruiz Arévalo 1:20 min)"
  - "Turnos establecidos por departamento de AVIANCA (testigo 1:27 min)"
  - "Actividades según manuales de AVIANCA (testigo 1:28 min)"
  - "AVIANCA designaba turnos y autorizaba cambios/permisos (testigo Sánchez Moreno 2:00 min)"
  - "Correos electrónicos de Jefe-Aseguramiento Calidad Operaciones Terrestres BOG al actor"
  - "Resolución 2017001587-CGPIVC: multa de 4000 SMMLV a cada demandada (Ministerio Trabajo)"
  - "Acuerdo de formalización laboral: AVIANCA se comprometió a vincular formalmente a los cooperados"
  - "Actor aparece en lista del acuerdo como integrante del área operaciones terrestres, cargo líder"
```

---

## [MAPPING_PYDANTIC]

### Schema `Salario`

```python
# Salario.sbl_por_anio → dict[int, Decimal]
# Fuente: [HISTORIAL_SALARIAL]
sbl_por_anio: dict[int, Decimal] = {
    2006: Decimal("997095"),
    2007: Decimal("763716"),
    2008: Decimal("1379251"),
    2009: Decimal("1929316"),
    2010: Decimal("2020339"),
    2011: Decimal("1983333"),
    2012: Decimal("2200417"),
    2013: Decimal("2274667"),
    2014: Decimal("2352500"),
    2015: Decimal("2663583"),
    2016: Decimal("2686666"),
    # 2017: bifurcado por concepto → ver notas en [REGLAS_SALARIO_BASE]
}

# Salario.historial_salarial → list[MesValor]
# Inferido de promedios anuales; valores mensuales no discriminados en fallo.
# Para meses de 2006–2010: usar sbl_por_anio[año] como valor constante del mes.
# NOTA: params/ipc_dane_mensual.json puede usarse para deflactar/indexar estos valores.
```

### Schema `LiquidacionInput.periodos_no_pagados`

```python
# list[PeriodoNoPagado]
# Fuente: [LIQUIDACION_CESANTIAS], [PRESCRIPCION]

periodos_no_pagados = [
    PeriodoNoPagado(
        concepto="cesantias",
        anio=2006, fecha_inicio="2006-09-01", fecha_fin="2006-12-31",
        dias=120, salario_base=Decimal("997095")
    ),
    PeriodoNoPagado(
        concepto="cesantias",
        anio=2007, fecha_inicio="2007-01-01", fecha_fin="2007-12-31",
        dias=360, salario_base=Decimal("763716")
    ),
    # ... (continuar para 2008–2016 con valores de [HISTORIAL_SALARIAL])
    PeriodoNoPagado(
        concepto="vacaciones_diferencia",
        fecha_inicio="2016-09-01", fecha_fin="2017-10-31",
        dias=Decimal("17.38"),
        salario_base=Decimal("2872211"),   # último salario — ver [REGLAS_SALARIO_BASE]
        ya_pagado=Decimal("1624600"),
        diferencia=Decimal("39367")
    ),
    PeriodoNoPagado(
        concepto="intereses_cesantias",
        fecha_inicio="2017-07-06", fecha_fin="2017-10-31",
        base=Decimal("2418475"),
        tasa=Decimal("0.038"),
        ya_pagado=Decimal("41195"),
        diferencia=Decimal("50707")
    ),
]
```

### Integración con archivos de parámetros externos

```yaml
params/ipc_dane_mensual.json:
  uso: >
    Indexar/actualizar montos históricos (2006–2017) a valores
    presentes si el motor requiere condena indexada.
    Los 204 índices mensuales cubren aprox. 17 años.
  nota: >
    El fallo ordena indexación de cesantías al momento del pago
    (fallo primera instancia lo señala). Aplicar IPC desde
    fecha de causación hasta fecha de pago efectivo.

params/2025.json y params/2026.json:
  uso: >
    SMMLV por año para validar salarios del período 2006–2010
    donde se tomó mínimo legal (folio 173–178 no discrimina
    salarios superiores al mínimo para esos años).
  nota: >
    Para 2006–2010, si no hay dato de salario superior probado,
    usar SMMLV del año correspondiente como salario base.
    La Corte confirmó este criterio del a quo.
```

---

## [HITOS_PROCESALES]

```yaml
cronologia:
  - fecha: "2006-05-01"
    hecho: "Inicio vínculo con Misión Temporal Ltda."
  - fecha: "2006-09-01"
    hecho: "Inicio vínculo via CTA Servicopava (convenio de asociación)"
  - fecha: "2009-02-05"
    hecho: "Contrato entre Servicopava y AVIANCA (oferta mercantil)"
  - fecha: "2017-08-31"
    hecho: "Resolución 2017001587-CGPIVC (multa Ministerio Trabajo)"
  - fecha: "2017-10-30"
    hecho: "Renuncia de Moreno Palma a Servicopava"
  - fecha: "2017-11-01"
    hecho: "Contrato de trabajo con SAI S.A.S. (empresa de AVIANCA Holdings)"
  - fecha: "2020-07-06"
    hecho: "Presentación demanda (interrumpe prescripción)"
  - fecha: "2022-10-10"
    hecho: "Audiencia conciliación — Bernal Ariza y Barreto Pinzón concilian"
  - fecha: "2023-03-13"
    hecho: "Sentencia primera instancia — Juzgado 22 Laboral Circuito Bogotá"
  - fecha: "2023-06-30"
    hecho: "Sentencia segunda instancia — Tribunal Superior Bogotá (revoca)"
  - fecha: "2024-09-17"
    hecho: "Sentencia CSJ SL2630-2024 (casa y modifica)"
```

---

## [JURISPRUDENCIA_CITADA]

```yaml
sentencias_relevantes:
  - id: "CSJ SL, 6 dic 2006, rad. 25713"
    tema: "Mala fe empresarial; uso fraudulento de CTAs"
  - id: "CSJ SL5595-2019"
    tema: "Personal misional permanente no puede vincularse vía CTAs intermediarias"
  - id: "CSJ SL4479-2020"
    tema: >
      Contratista independiente debe tener estructura propia y aparato
      productivo especializado. Sin eso = intermediario.
  - id: "CSJ SL2084-2023"
    tema: "Sistematización de indicios de intermediación laboral ilegal"
  - id: "CSJ SL3777-2022"
    tema: >
      No ser dueños de medios de producción = indicio de vínculo
      asociado aparente.
  - id: "CSJ SL2885-2019"
    tema: "Sentencia de contrato realidad es declarativa (no constitutiva)"
  - id: "CSJ SL1715-2024"
    tema: "Procedencia compensación de pagos en contratos realidad vía CTA"
  - id: "CSJ SL3570-2020"
    tema: "Compensación pagos CTA vs. prestaciones laborales"
  - id: "CSJ SL, 27 jul 2001, rad. 16074"
    tema: "Salario base de liquidación cesantías — régimen Ley 50/1990"
  - id: "CSJ SL, 6 oct 2006, rad. 28718"
    tema: "Base de compensación monetaria de vacaciones = último salario"
  - id: "CSJ SL2726-2022"
    tema: "Excepción de compensación en contratos realidad CTA"
  - id: "CSJ SL460-2021"
    tema: "Criterios contrato realidad (citada por a quo)"
  - id: "CSJ SL3436-2021"
    tema: "Integración del trabajador a la organización como indicio laboral"
```

---

## [GLOSARIO]

| ID | Término | Definición en contexto |
|----|---------|----------------------|
| `CTA` | Cooperativa de Trabajo Asociado | Figura jurídica que vincula el trabajo personal de sus asociados para producción/servicios. Debe operar con plena autonomía técnica, administrativa y financiera. |
| `CONTRATO_REALIDAD` | Contrato de trabajo realidad | Aplicación del principio de primacía de la realidad: cuando los hechos revelan subordinación independientemente de la forma contractual adoptada. |
| `SUBORDINACION` | Subordinación laboral | Elemento esencial del contrato de trabajo; poder del empleador de impartir órdenes y el deber del trabajador de acatarlas. Diferente a la coordinación cooperativa. |
| `INTERMEDIARIO_LABORAL` | Simple intermediario | Entidad que, sin ser verdadero empleador, interpone para vincular formalmente trabajadores a disposición de la empresa principal. Responde solidariamente. |
| `ACTIVIDAD_MISIONAL_PERMANENTE` | Actividad misional permanente | Funciones directamente relacionadas con la producción del bien o servicio característico de la empresa (Decreto 2025/2011 art. 1). |
| `PRESCRIPCION` | Prescripción laboral | Extinción del derecho por inactividad del titular. Plazo: 3 años desde exigibilidad (art. 488 CST). |
| `SBL` | Salario base de liquidación | Valor salarial usado como base para calcular cada prestación social según la norma aplicable. |
| `IBC` | Ingreso base de cotización | Valor reportado a seguridad social; usado en este fallo como proxy del salario real cuando no hay otra prueba. |
| `COMODATO_PRECARIO` | Comodato precario | Entrega de bienes (equipos, herramientas) a título de préstamo gratuito. En este caso AVIANCA entregó equipos a Servicopava en comodato — no implica subordinación per se, pero es indicio de falta de autonomía de la CTA. |
| `SMMLV` | Salario Mínimo Mensual Legal Vigente | Valor mínimo del salario fijado anualmente. Usado como base para periodos 2006–2010 donde no se probó salario superior. |
| `EXCEPCION_COMPENSACION` | Excepción de compensación | Mecanismo por el cual se descuentan los pagos ya recibidos (compensaciones CTA) del total de prestaciones laborales reconocidas, para evitar doble pago. |
| `AD_QUEM` | Ad quem | Juez de segunda instancia (Tribunal Superior de Bogotá en este caso). |
| `A_QUO` | A quo | Juez de primera instancia (Juzgado 22 Laboral del Circuito de Bogotá). |
| `SUB_LITE` | Sub lite | El asunto bajo análisis / el caso concreto. |
| `AVANCEMOS` | Plataforma AVANCEMOS | Plataforma tecnológica de AVIANCA de obligatorio cumplimiento para los cooperados — evidencia de subordinación. |
| `SAI` | Servicios Aeroportuarios Integrados S.A.S. | Empresa del grupo AVIANCA Holdings a la que se vinculó formalmente el actor desde 2017-11-01. |

---

## [DATOS_NO_DISPONIBLES_EN_FALLO]

```yaml
# Datos que el motor debe obtener de fuentes externas
datos_externos_requeridos:
  - campo: "SMMLV 2006–2016"
    fuente: "params/2025.json o params/2026.json"
    uso: "Validar/complementar salarios base cuando IBC no discrimina"

  - campo: "IPC DANE mensual 2006–2024"
    fuente: "params/ipc_dane_mensual.json"
    uso: "Indexar cesantías y demás condenas al momento del pago efectivo"

  - campo: "Tasa intereses cesantías definitiva"
    fuente: "Norma / params externos"
    uso: >
      El fallo aplica 3.8% para el período jul-oct 2017.
      Verificar si corresponde a DTF o tasa legal vigente para otros periodos.

  - campo: "Histórico compensaciones mensuales 2006–2015"
    fuente: "Folios 173–184 del expediente (no transcritos en sentencia)"
    uso: >
      Para aplicar excepción de compensación en periodos anteriores
      a 2016, se necesitan los valores reales pagados por la CTA.
      El fallo no los discrimina año a año más allá de lo expuesto.
```

---

*Documento generado como base de conocimiento para consumo por agente IA. Fuente única: Sentencia CSJ SL2630-2024, Radicación 101342, Acta 34, 2024-09-17.*
