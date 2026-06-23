# KB: CONTRATO DE PRESTACIÓN DE SERVICIOS — VÍNCULO LABORAL
> Base de conocimiento estructurada para agente de IA  
> Fuente: `CONTRATO.pdf` | Generada: 2025-06-23  
> Propósito: Evaluar impacto operacional y tomar decisiones sobre el repositorio de la finca

---

## ÍNDICE RÁPIDO

| Si necesitas saber sobre... | Ir a sección |
|-----------------------------|--------------|
| Quiénes son las partes | [`[PARTES]`](#partes) |
| Vigencia y fechas críticas | [`[VIGENCIA]`](#vigencia) |
| Compensación económica total | [`[COMPENSACION]`](#compensacion) |
| Obligaciones operacionales del contratista | [`[OBLIGACIONES_OPERATIVAS]`](#obligaciones_operativas) |
| Servicios públicos y quién paga qué | [`[SERVICIOS_PUBLICOS]`](#servicios_publicos) |
| Seguridad social | [`[SEGURIDAD_SOCIAL]`](#seguridad_social) |
| Restricciones y prohibiciones | [`[RESTRICCIONES]`](#restricciones) |
| Resolución de conflictos | [`[CONTROVERSIAS]`](#controversias) |
| Glosario de términos | [`[GLOSARIO]`](#glosario) |
| Plantillas de decisión | [`[PLANTILLAS]`](#plantillas) |
| Alertas críticas para el agente | [`[ALERTAS]`](#alertas) |

---

## [PARTES] {#partes}

```yaml
contratante:
  rol: Propietaria de la finca / quien paga
  nombre: HILDALIRIA RAIGOZA LOAIZA
  cc: "42066783"
  telefono: "+1 (239) 285-0767"
  correo: ralo5353@gmail.com
  obligaciones_principales:
    - Pagar salario mensual
    - Pagar compensación de $300.000 por ordeño domingos/festivos
    - Pagar acueducto
    - Compensar energía con $55.000/mes
    - Verificar pago de seguridad social antes de cada desembolso

contratista:
  rol: Prestador de servicios / operador de la finca
  nombre: PEDRO LUIS GIRALDO FRANCO
  cc: "7.247.867"
  telefono: "320 6904739"
  correo: yuyisgiraldo@hotmail.com
  obligaciones_principales:
    - Ejecutar todas las labores operativas de la finca
    - Pagar su proporción de seguridad social
    - Pagar energía, internet y gas domiciliario
    - No permitir ingreso de terceros no autorizados a potreros/establo

predio:
  nombre_1: Lote 1 El Venado
  nombre_2: Lote 2 La Isabella II
  sector: Las Mangas
  municipio: Santa Rosa de Cabal
  departamento: Risaralda
  actividad_principal: Ganadería y actividades conexas
```

---

## [VIGENCIA] {#vigencia}

```yaml
fecha_inicio: 2025-05-15
duracion: 1 año
fecha_fin_inicial: 2026-05-15
renovacion: automática al vencer el período
condicion_no_renovacion: cualquiera de las partes debe notificar con 30 días calendario de antelación

fechas_criticas:
  - fecha: 2026-04-15
    evento: Fecha límite para notificar NO renovación (30 días antes del vencimiento)
    prioridad: ALTA
  - fecha: 2026-05-15
    evento: Vencimiento del contrato / inicio de renovación automática si no hay notificación
    prioridad: ALTA
```

> **NOTA PARA EL AGENTE:** Hoy es 2026-06-23. El contrato ya venció el 2026-05-15. Si no hubo notificación de no-renovación antes del 2026-04-15, el contrato se renovó automáticamente por otro año (hasta 2027-05-15). **Verificar estado actual de renovación.**

---

## [COMPENSACION] {#compensacion}

### Salario base

| Concepto | Valor 2025 | Ajuste |
|----------|-----------|--------|
| Salario mínimo legal mensual vigente | $1.423.500 COP | Ajuste anual por IPC según decreto gobierno nacional |

### Compensaciones adicionales

| Concepto | Valor mensual | Condición |
|----------|--------------|-----------|
| Ordeño y distribución de leche (domingos y festivos) | $300.000 COP | Fija, no condicional |
| Compensación energía eléctrica | $55.000 COP | Pagada por contratante al contratista |

### Resumen económico mensual (a cargo de la contratante)

```yaml
pago_mensual_contratante:
  salario_base: 1_423_500  # COP, vigencia 2025
  compensacion_ordeño_festivos: 300_000
  compensacion_energia: 55_000
  total_mensual_minimo: 1_778_500  # COP
  nota: "El salario base se ajusta cada año por IPC. Las compensaciones son fijas según contrato."

gastos_cargo_contratista:
  - energia_electrica  # descuenta los $55.000 recibidos
  - internet
  - gas_domiciliario
  - proporcion_seguridad_social_segun_ley
```

---

## [OBLIGACIONES_OPERATIVAS] {#obligaciones_operativas}

### Funciones del contratista (con clasificación de dominio)

| ID | Función | Dominio | Frecuencia |
|----|---------|---------|-----------|
| F-01 | Ordeño de ganado vacuno bovino | Ganadería | Diaria (incluye domingos/festivos) |
| F-02 | Pastoreo de ganado vacuno bovino | Ganadería | Diaria |
| F-03 | Cuidado de todos los animales de la finca (alimento, bebida, medicina, aseo, hábitat) | Animal general | Permanente |
| F-04 | Mantenimiento y cuidado de potreros | Infraestructura | Periódica |
| F-05 | Mantenimiento de huertas caseras y otros productos | Agricultura | Periódica |
| F-06 | Cuidado y uso de herramientas e inventario de la finca | Logística | Permanente |
| F-07 | Deshierbado, guadañada y fumigación | Mantenimiento | Según necesidad |
| F-08 | Vigilancia de cosechas | Seguridad interna | Permanente |
| F-09 | Venta y registro de productos agrícolas (leche, huevos, derivados, plátano, frutales, hortalizas) | Comercial/Administrativo | Continua |
| F-10 | Reporte al propietario sobre ventas y producción | Comunicación | Continua |
| F-11 | Conservación y cuidado general de la finca | General | Permanente |
| F-12 | Cuidado de plantas ornamentales y huerta en general | Jardinería | Permanente |
| F-13 | Aviso previo de ausencias por salud o diligencias personales | Administrativo | Cuando aplique |
| F-14 | Designar persona de confianza para cuidado de finca durante ausencias | Gestión de contingencia | Cuando aplique |

### Inventario de herramientas

```yaml
inventario_herramientas:
  estado: "Referenciado en hoja adjunta al contrato (no incluida en este PDF)"
  nota_agente: "El inventario forma parte integral del contrato. Solicitar documento adjunto para auditoría."
  responsable: contratista
```

---

## [SERVICIOS_PUBLICOS] {#servicios_publicos}

| Servicio | Responsable del pago | Compensación recibida |
|----------|---------------------|-----------------------|
| Acueducto | Contratante (propietaria) | N/A |
| Energía eléctrica | Contratista | $55.000/mes de la contratante |
| Internet | Contratista | Ninguna |
| Gas domiciliario | Contratista | Ninguna |

---

## [SEGURIDAD_SOCIAL] {#seguridad_social}

```yaml
seguridad_social:
  responsable_pago: contratista (proporción que ordena la ley)
  control_previo:
    quién_verifica: contratante
    cuándo: antes de cada pago salarial
    qué_verifica: planilla del período correspondiente
  consecuencia_mora: riesgo para integridad física y mental del contratista (explicitado en contrato)
  nota_legal: "La verificación previa es obligación contractual de la contratante, no facultativa."
```

---

## [RESTRICCIONES] {#restricciones}

```yaml
restriccion_acceso_terceros:
  zona_restringida:
    - sector de potreros
    - establo
  autorización_requerida: sí — por parte del contratista
  consecuencia_incumplimiento:
    responsable: contratista
    alcance: "Asume por su cuenta y riesgo cualquier suceso sobre los terceros no autorizados"
    exoneración_contratante: total (pagos e indemnizaciones)

derecho_vivienda:
  titular: contratista
  ubicación: dentro de la finca objeto del contrato
  tipo: incluido en el contrato, no remunerado adicionalmente
```

---

## [CONTROVERSIAS] {#controversias}

```yaml
resolucion_conflictos:
  jurisdiccion: Ordinaria (civil)
  instancia: Jurisdicción Ordinaria
  nota: "No se pactó arbitramento ni mediación previa. Conflictos van directamente a juez civil."
```

---

## [GLOSARIO] {#glosario}

| ID | Término | Definición en contexto |
|----|---------|------------------------|
| `G-SMMLV` | Salario Mínimo Legal Mensual Vigente | Base de remuneración fijada anualmente por el gobierno colombiano. En 2025: $1.423.500 COP |
| `G-IPC` | Índice de Precios al Consumidor | Indicador de inflación usado para ajustar el salario anualmente |
| `G-CONTRATANTE` | Contratante | HILDA LIRIA RAIGOZA LOAIZA — propietaria de la finca, quien comisiona y paga los servicios |
| `G-CONTRATISTA` | Contratista | PEDRO LUIS GIRALDO FRANCO — prestador de servicios, operador de campo |
| `G-PREDIO` | Predio | Propiedad rural objeto del contrato (Lote 1 El Venado + Lote 2 La Isabella II) |
| `G-PRORROGA` | Prórroga automática | Renovación del contrato sin necesidad de nuevo documento, salvo aviso de no renovación |
| `G-PLANILLA` | Planilla de seguridad social | Documento de pago de aportes a salud y pensión, verificado mensualmente |
| `G-FINCA` | Finca | Término genérico para el predio rural con actividad ganadera y agrícola |

---

## [PLANTILLAS] {#plantillas}

### Plantilla: Evaluación de renovación contractual

```yaml
evaluacion_renovacion:
  fecha_evaluacion: "{{FECHA_HOY}}"
  contrato_ref: "Contrato Raigoza-Giraldo, firmado 2025-05-15"
  
  estado_vigencia:
    vencimiento_original: "2026-05-15"
    notificacion_no_renovacion_enviada: "{{SI/NO}}"
    fecha_notificacion: "{{FECHA O NULL}}"
    estado_actual: "{{RENOVADO_AUTO / VENCIDO / EN_NEGOCIACION}}"
    nueva_fecha_vencimiento: "{{FECHA SI RENOVADO}}"
  
  cumplimiento_obligaciones_contratante:
    salario_pagado_al_dia: "{{SI/NO}}"
    compensacion_festivos_pagada: "{{SI/NO}}"
    acueducto_pagado: "{{SI/NO}}"
    compensacion_energia_pagada: "{{SI/NO}}"
    verificacion_seguridad_social: "{{SI/NO}}"
  
  cumplimiento_obligaciones_contratista:
    funciones_operativas_al_dia: "{{SI/NO}}"
    seguridad_social_al_corriente: "{{SI/NO}}"
    inventario_herramientas_integro: "{{SI/NO}}"
    acceso_terceros_controlado: "{{SI/NO}}"
  
  decision_recomendada: "{{RENOVAR / NO_RENOVAR / RENEGOCIAR}}"
  justificacion: "{{TEXTO}}"
```

### Plantilla: Registro mensual de pagos

```yaml
pago_mensual:
  mes: "{{MES_AÑO}}"
  contratista: "Pedro Luis Giraldo Franco"
  
  conceptos:
    salario_base: 1_423_500  # Actualizar si hay ajuste IPC
    compensacion_festivos: 300_000
    compensacion_energia: 55_000
    total_a_pagar: "{{CALCULAR}}"
  
  verificacion_previa:
    planilla_seguridad_social_presentada: "{{SI/NO}}"
    periodo_cubierto: "{{MES}}"
    fecha_verificacion: "{{FECHA}}"
  
  estado_pago: "{{PENDIENTE / PAGADO}}"
  fecha_pago: "{{FECHA O NULL}}"
```

### Plantilla: Reporte de incidente (restricción de acceso)

```yaml
incidente_acceso_no_autorizado:
  fecha: "{{FECHA}}"
  zona_afectada: "{{POTREROS / ESTABLO}}"
  tercero_involucrado: "{{NOMBRE O DESCRIPCION}}"
  autorizado_por_contratista: "{{SI/NO}}"
  descripcion_suceso: "{{TEXTO}}"
  responsabilidad_asumida_por: "{{CONTRATISTA segun clausula 6}}"
  accion_tomada: "{{TEXTO}}"
```

---

## [ALERTAS] {#alertas}

> Alertas críticas que el agente debe evaluar en cada consulta:

```yaml
alertas_criticas:
  
  - id: ALERTA-001
    tipo: TEMPORAL
    prioridad: ALTA
    descripcion: "El contrato original venció el 2026-05-15. Hoy es 2026-06-23."
    pregunta_clave: "¿Se notificó no-renovación antes del 2026-04-15?"
    si_no_se_notifico: "El contrato se renovó automáticamente hasta 2027-05-15"
    accion_requerida: "Confirmar estado de renovación con las partes"

  - id: ALERTA-002
    tipo: FINANCIERO
    prioridad: MEDIA
    descripcion: "El salario base debe ajustarse por IPC cada año. Verificar si se aplicó ajuste para 2026."
    base_2025: 1_423_500
    accion_requerida: "Consultar SMMLV 2026 y actualizar monto en registros"

  - id: ALERTA-003
    tipo: OPERACIONAL
    prioridad: ALTA
    descripcion: "El inventario de herramientas es documento adjunto integral al contrato."
    accion_requerida: "Localizar y digitalizar hoja de inventario para auditoría completa"

  - id: ALERTA-004
    tipo: LEGAL
    prioridad: MEDIA
    descripcion: "La verificación de planilla de seguridad social debe hacerse ANTES de cada pago."
    consecuencia_omision: "La contratante incurre en incumplimiento contractual"
    accion_requerida: "Establecer flujo de verificación mensual documentado"

  - id: ALERTA-005
    tipo: CLASIFICACION_LABORAL
    prioridad: ALTA
    descripcion: "Contrato denominado 'prestación de servicios', pero incluye vivienda, funciones permanentes 24/7 y subordinación operativa. Posible riesgo de recaracterización como contrato laboral por juez ordinario."
    accion_requerida: "Consultar asesoría jurídica laboral sobre exposición real"
```

---

## [ARQUITECTURA_OPERACIONAL] {#arquitectura_operacional}

```
FINCA (Santa Rosa de Cabal, Risaralda)
├── Lote 1: El Venado
└── Lote 2: La Isabella II (Las Mangas)
         │
         ▼
CONTRATISTA (Pedro Luis Giraldo Franco) — reside en finca
    │
    ├─── Ganadería ──→ Ordeño → Venta leche/derivados → Reporte a propietaria
    │
    ├─── Agricultura ─→ Huertas/frutales/plátano → Venta → Reporte
    │
    ├─── Mantenimiento ─→ Potreros / guadaña / fumigación / ornamentales
    │
    └─── Administración ─→ Inventario herramientas / Control acceso / Avisos ausencia
         │
         ▼
CONTRATANTE (Hilda Liria Raigoza Loaiza) — remota (teléfono EE.UU.)
    │
    ├─── Paga: salario + compensaciones + acueducto
    └─── Controla: verificación planilla SS antes de cada pago
```

---

*Fin del documento de base de conocimiento.*  
*Versión generada automáticamente desde `CONTRATO.pdf` para uso de agente de IA.*
