# Análisis de Arquitectura y Estructura de Archivos
## Sistema de Liquidación de Nómina Colombia 2025

Arquitectura completa necesaria para implementar el sistema. A continuación presento la estructura de archivos, módulos y componentes necesarios.

---

## **ESTRUCTURA DE DIRECTORIOS COMPLETA**

```
liquidacion_cli/
│
├── bin/
│   └── liquidar                          # Script ejecutable principal (CLI entry point)
│
├── liquidator/                           # Package principal de Python
│   ├── __init__.py
│   │
│   ├── core/                             # Módulos centrales del motor de cálculo
│   │   ├── __init__.py
│   │   ├── engine.py                     # Motor principal de orquestación
│   │   ├── input_parser.py               # Parseo y validación de entradas
│   │   └── workflow_orchestrator.py      # Orquestación de flujos (periódica/finiquito)
│   │
│   ├── calculators/                      # Módulos de cálculo específicos
│   │   ├── __init__.py
│   │   ├── sbl_calculator.py             # Cálculo de SBL (General, Vacaciones, Prima)
│   │   ├── prestaciones_calculator.py    # Cesantías, intereses, prima
│   │   ├── vacaciones_calculator.py      # Cálculo específico de vacaciones
│   │   ├── indemnizacion_calculator.py   # Indemnizaciones (para finiquito)
│   │   └── salario_pendiente_calculator.py # Salarios adeudados
│   │
│   ├── validators/                       # Validadores de datos y reglas de negocio
│   │   ├── __init__.py
│   │   ├── input_validator.py            # Validación de datos de entrada
│   │   ├── contract_validator.py         # Validación de tipo de contrato
│   │   ├── date_validator.py             # Validación de fechas y periodos
│   │   └── salary_validator.py           # Validación de componentes salariales
│   │
│   ├── compliance/                       # Sistema de cumplimiento legal
│   │   ├── __init__.py
│   │   ├── compliance_engine.py          # Motor principal de cumplimiento
│   │   ├── checklist_loader.py           # Carga y parseo del checklist legal
│   │   ├── rule_evaluator.py             # Evaluación de reglas individuales
│   │   ├── report_generator.py           # Generación de reportes de cumplimiento
│   │   └── override_manager.py           # Gestión de overrides humanos
│   │
│   ├── legal/                            # Referencias legales y normativas
│   │   ├── __init__.py
│   │   ├── normas_repository.py          # Repositorio de normas legales
│   │   ├── plazos_manager.py             # Gestión de plazos legales
│   │   ├── topes_manager.py              # Gestión de topes y límites legales
│   │   └── recargos_manager.py           # Gestión de recargos (dominical, nocturno, etc.)
│   │
│   ├── params/                           # Gestión de parámetros oficiales
│   │   ├── __init__.py
│   │   ├── params_loader.py              # Carga de parámetros desde archivos
│   │   ├── params_validator.py           # Validación de parámetros
│   │   └── params_versioning.py          # Control de versiones de parámetros
│   │
│   ├── output/                           # Generadores de salida
│   │   ├── __init__.py
│   │   ├── json_generator.py             # Generación de JSON estructurado
│   │   ├── markdown_generator.py         # Generación de documentos Markdown
│   │   ├── pdf_generator.py              # Generación de PDFs
│   │   └── template_manager.py           # Gestión de plantillas de documentos
│   │
│   ├── audit/                            # Sistema de auditoría y trazabilidad
│   │   ├── __init__.py
│   │   ├── audit_logger.py               # Registro de eventos de auditoría
│   │   ├── hash_calculator.py            # Cálculo de hashes para verificación
│   │   ├── versioning_manager.py         # Gestión de versiones de cálculos
│   │   └── trail_generator.py            # Generación de audit trail
│   │
│   ├── utils/                            # Utilidades generales
│   │   ├── __init__.py
│   │   ├── date_utils.py                 # Utilidades de manejo de fechas
│   │   ├── currency_utils.py             # Formateo y redondeo de moneda
│   │   ├── file_utils.py                 # Operaciones de archivos
│   │   └── error_handler.py              # Manejo centralizado de errores
│   │
│   └── tests/                            # Suite de pruebas
│       ├── __init__.py
│       ├── test_calculators/
│       │   ├── test_sbl.py
│       │   ├── test_prestaciones.py
│       │   └── test_vacaciones.py
│       ├── test_compliance/
│       │   ├── test_checklist.py
│       │   ├── test_validations.py
│       │   └── test_override.py
│       ├── test_integration/
│       │   ├── test_periodica.py
│       │   ├── test_finiquito.py
│       │   └── test_edge_cases.py
│       ├── fixtures/                     # Datos de prueba
│       │   ├── example_periodica.json
│       │   ├── example_finiquito.json
│       │   └── edge_cases/
│       └── test_examples.py
│
├── params/                               # Archivos de parámetros legales
│   ├── 2025.json                         # Parámetros oficiales 2025
│   ├── 2024.json                         # Parámetros históricos (para referencia)
│   ├── normas.json                       # Referencias normativas completas
│   ├── plazos.json                       # Plazos legales de pago
│   └── schema.json                       # Schema de validación de parámetros
│
├── legal_docs/                           # Documentación legal de referencia
│   ├── CST_articulos_relevantes.md       # Artículos del CST aplicables
│   ├── leyes_vigentes.md                 # Leyes y decretos vigentes
│   ├── jurisprudencia_relevante.md       # Jurisprudencia aplicable
│   └── checklist_cumplimiento.md         # CHECKLIST completo de cumplimiento
│
├── templates/                            # Plantillas de documentos
│   ├── comprobante_periodica.md          # Plantilla para liquidación periódica
│   ├── comprobante_finiquito.md          # Plantilla para finiquito
│   ├── styles/
│   │   └── pdf_styles.css                # Estilos para generación de PDF
│   └── partials/
│       ├── header.md
│       ├── footer.md
│       └── firmas.md
│
├── audit/                                # Directorio de auditoría (generado)
│   ├── logs/                             # Logs de ejecución
│   ├── trails/                           # Audit trails por ejecución
│   └── reports/                          # Reportes de cumplimiento guardados
│
├── examples/                             # Ejemplos de uso
│   ├── example_finca_rural.json          # Caso específico de finca rural
│   ├── example_salario_variable.json     # Caso de salario variable
│   ├── example_finiquito.json            # Ejemplo de finiquito
│   └── README_examples.md                # Documentación de ejemplos
│
├── docs/                                 # Documentación del proyecto
│   ├── architecture.md                   # Arquitectura del sistema
│   ├── api_reference.md                  # Referencia de API interna
│   ├── legal_compliance.md               # Documentación de cumplimiento legal
│   ├── user_guide.md                     # Guía de usuario
│   └── developer_guide.md                # Guía para desarrolladores
│
├── config/                               # Configuraciones del sistema
│   ├── default_config.yaml               # Configuración por defecto
│   ├── compliance_policies.yaml          # Políticas de cumplimiento
│   └── logging_config.yaml               # Configuración de logging
│
├── scripts/                              # Scripts auxiliares
│   ├── update_params.py                  # Script para actualizar parámetros anuales
│   ├── validate_compliance.py            # Validador independiente de cumplimiento
│   └── generate_test_data.py             # Generador de datos de prueba
│
├── .gitignore
├── requirements.txt                      # Dependencias Python
├── requirements-dev.txt                  # Dependencias de desarrollo
├── setup.py                              # Configuración de instalación
├── pytest.ini                            # Configuración de pytest
├── README.md                             # Documentación principal
└── LICENSE                               # Licencia del software
```

---

## **ARQUITECTURA DE COMPONENTES**

### **1. CAPA DE ENTRADA (Input Layer)**

**Componentes:**
- `bin/liquidar` - CLI entry point
- `liquidator/core/input_parser.py` - Parseo de JSON/flags
- `liquidator/validators/input_validator.py` - Validación de esquema

**Responsabilidades:**
- Parsear argumentos de CLI y archivos JSON
- Validar estructura de entrada
- Normalizar datos para procesamiento interno
- Manejar errores de entrada tempranamente

**Interfaces clave:**
```python
# Estructura de entrada esperada
InputData = {
    "modo": str,                          # "PERIODICA" | "FINIQUITO"
    "fecha_ingreso": str,                 # "YYYY-MM-DD"
    "fecha_corte": str,                   # "YYYY-MM-DD"
    "salario_mensual": int,               # COP
    "salarios_historicos": List[Dict],    # Opcional
    "comisiones_promedio_mensual": float,
    "horas_extras_promedio_mensual": float,
    "bonificaciones_promedio_mensual": float,
    "reside_en_lugar_trabajo": bool,
    "auxilio_conectividad": int,
    "dias_vacaciones_pendientes": int,
    "tipo_contrato": str,
    "enforce-compliance": bool,
    "compliance-policy": str,
    "human-override": bool,
    "operator-id": str,
    "override-reason": str
}
```

---

### **2. CAPA DE PARÁMETROS LEGALES (Legal Parameters Layer)**

**Componentes:**
- `liquidator/params/params_loader.py` - Carga de parámetros
- `liquidator/legal/normas_repository.py` - Repositorio de normas
- `liquidator/legal/plazos_manager.py` - Gestión de plazos
- `liquidator/legal/topes_manager.py` - Gestión de topes

**Responsabilidades:**
- Cargar parámetros oficiales del año vigente
- Proveer acceso a referencias normativas
- Gestionar plazos legales de pago
- Aplicar topes y límites legales

**Archivos de datos requeridos:**

**params/2025.json:**
```json
{
  "version": "2025-10-31",
  "vigencia_desde": "2025-01-01",
  "vigencia_hasta": "2025-12-31",
  "parametros": {
    "SMMLV": 1423500,
    "AUXILIO_TRANS": 200000,
    "LIMITE_AUXILIO_FACTOR": 2,
    "TASA_INT_CESANTIAS": 0.12,
    "DIAS_BASE": 360.0,
    "VACACIONES_DENOM": 720.0,
    "REDONDEO": 0,
    "TOPE_INDEMNIZACION_SMMLV": 20,
    "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01"
  },
  "referencias": {
    "SMMLV": "Decreto 1572/2024",
    "AUXILIO_TRANS": "Decreto 1573/2024",
    "TASA_INT_CESANTIAS": "Ley 50/1990 Art.99"
  }
}
```

**params/normas.json:**
```json
{
  "normas": [
    {
      "id": "CST_249_250",
      "nombre": "Código Sustantivo del Trabajo Arts. 249-250",
      "descripcion": "Cesantías - Régimen de liquidación",
      "texto_relevante": "Todo empleador está obligado a pagar...",
      "url": "https://...",
      "vigencia": "permanente"
    },
    {
      "id": "LEY50_99",
      "nombre": "Ley 50 de 1990 Art. 99",
      "descripcion": "Intereses sobre cesantías",
      "tasa": 0.12,
      "url": "https://...",
      "vigencia": "permanente"
    }
    // ... más normas
  ],
  "plazos_pago": {
    "cesantias": {
      "dia": 14,
      "mes": 2,
      "descripcion": "14 de febrero del año siguiente",
      "norma_ref": "CST_249_250"
    },
    "intereses_cesantias": {
      "dia": 31,
      "mes": 1,
      "descripcion": "31 de enero del año siguiente",
      "norma_ref": "LEY50_99"
    },
    "prima_junio": {
      "dia": 30,
      "mes": 6,
      "descripcion": "30 de junio",
      "norma_ref": "CST_306_308"
    },
    "prima_diciembre": {
      "dia": 20,
      "mes": 12,
      "descripcion": "20 de diciembre",
      "norma_ref": "CST_306_308"
    }
  }
}
```

**params/plazos.json:**
```json
{
  "plazos_pago_inmediato": {
    "finiquito": {
      "descripcion": "Pago inmediato al terminar el contrato",
      "max_dias": 1,
      "norma_ref": "CST_65"
    }
  },
  "plazos_consignacion": {
    "cesantias": {
      "tipo": "anual",
      "fecha_limite": "02-14",
      "descripcion": "Consignar en fondo antes del 14 de febrero"
    }
  }
}
```

---

### **3. CAPA DE CÁLCULO (Calculation Layer)**

**Componentes principales:**

#### **3.1 SBL Calculator (`liquidator/calculators/sbl_calculator.py`)**

**Responsabilidades:**
- Calcular SBL_GENERAL (para cesantías, intereses, prima)
- Calcular SBL_VACACIONES (excluyendo extras y auxilios)
- Aplicar reglas de auxilio de transporte/conectividad
- Manejar salarios variables (promedios)

**Métodos clave:**
```python
class SBLCalculator:
    def calculate_sbl_general(input_data, params) -> float
    def calculate_sbl_vacaciones(input_data, params) -> float
    def calculate_sbl_prima(input_data, params) -> float
    def apply_auxilio_rules(input_data, params) -> Dict[str, Any]
    def calculate_promedio_variable(salarios_historicos, meses) -> float
```

**Reglas específicas a implementar:**
- Exclusión de auxilio de transporte si `reside_en_lugar_trabajo == True`
- Verificación de límite salarial (2 SMMLV) para auxilio
- Promediación de últimos 12 meses para salarios variables
- Alerta si auxilio de conectividad no está pactado como salario

#### **3.2 Prestaciones Calculator (`liquidator/calculators/prestaciones_calculator.py`)**

**Responsabilidades:**
- Calcular cesantías con base 360 días
- Calcular intereses sobre cesantías (12% anual)
- Calcular prima de servicios (proporcional por semestre)
- Determinar días liquidables por concepto

**Fórmulas a implementar:**
```python
# Cesantías
cesantias = (SBL_GENERAL * dias_servicio) / 360

# Intereses sobre cesantías
intereses = (cesantias * dias_servicio * 0.12) / 360

# Prima de servicios
dias_prima = calcular_dias_semestre(fecha_ingreso, fecha_corte)
prima = (SBL_PRIMA * dias_prima) / 360
```

#### **3.3 Vacaciones Calculator (`liquidator/calculators/vacaciones_calculator.py`)**

**Responsabilidades:**
- Calcular días de vacaciones causadas
- Calcular valor monetario de vacaciones (base 720)
- Determinar si aplica compensación en dinero (solo finiquito)

**Reglas específicas:**
- En modo PERIÓDICA: no incluir vacaciones en liquidación
- En modo FINIQUITO: compensar vacaciones pendientes
- Base de cálculo: SBL_VACACIONES (sin extras ni auxilios)

#### **3.4 Indemnización Calculator (`liquidator/calculators/indemnizacion_calculator.py`)**

**Responsabilidades:**
- Calcular indemnización por terminación sin justa causa
- Aplicar tope de 20 SMMLV
- Diferenciar entre contratos indefinidos y a término fijo

**Reglas específicas:**
- Tope máximo: 20 SMMLV (Art. 64 CST)
- Fórmula depende del tipo de contrato y tiempo de servicio
- Solo aplica en modo FINIQUITO

---

### **4. CAPA DE CUMPLIMIENTO LEGAL (Compliance Layer)**

**Componentes principales:**

#### **4.1 Compliance Engine (`liquidator/compliance/compliance_engine.py`)**

**Responsabilidades:**
- Orquestar todas las validaciones de cumplimiento
- Determinar estado final: GO / NO_GO
- Generar reporte completo de cumplimiento

**Workflow:**
```
1. Cargar checklist de cumplimiento
2. Ejecutar validaciones individuales
3. Evaluar severidad de cada resultado
4. Determinar bloqueos (failures vs warnings)
5. Generar reporte estructurado
6. Manejar overrides humanos si aplican
```

#### **4.2 Checklist Loader (`liquidator/compliance/checklist_loader.py`)**

**Responsabilidades:**
- Cargar y parsear el CHECKLIST de cumplimiento legal
- Convertir reglas en objetos ejecutables
- Mantener referencias normativas

**Estructura del checklist:**
```python
ChecklistRule = {
    "id": str,                    # V001, V002, etc.
    "description": str,
    "severity": str,              # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    "rule_type": str,             # "validation" | "calculation" | "documentation"
    "rule_ref": List[str],        # Referencias normativas
    "evaluator": Callable         # Función que ejecuta la validación
}
```

#### **4.3 Rule Evaluator (`liquidator/compliance/rule_evaluator.py`)**

**Responsabilidades:**
- Ejecutar validaciones individuales
- Recolectar evidencia de cumplimiento/incumplimiento
- Asignar resultados: PASS / WARN / FAIL

**Validaciones a implementar (según CHECKLIST):**

**V001: Parámetros oficiales 2025**
- Verificar SMMLV = 1423500
- Verificar AUXILIO_TRANS = 200000
- Verificar coherencia de todos los parámetros

**V002: Contrato válido**
- Rechazar contratos de prestación de servicios
- Validar tipos de contrato reconocidos

**V003: Auxilio transporte aplicado correctamente**
- Verificar exclusión si `reside_en_lugar_trabajo == True`
- Verificar límite de 2 SMMLV

**V004: Fórmulas de cesantías correctas**
- Validar cálculo contra fórmula legal
- Verificar base 360 días

**V005: Intereses de cesantías tasa correcta**
- Validar tasa 12% anual

**V006: Prima semestre proporcional**
- Validar días liquidados del semestre
- Verificar proporcionalidad

**V007: Vacaciones excluidas en periódica**
- Verificar que vacaciones = 0 en modo PERIÓDICA

**V008: Plazos de pago documentados**
- Verificar presencia de `plazo_pago_legal` en cada concepto

**V009: Sustento legal presente**
- Verificar que cada concepto incluya `norma` y `referencia`

**V010: Hashes y versionamiento**
- Verificar presencia de `params_version`, `input_hash`, `output_hash`

#### **4.4 Override Manager (`liquidator/compliance/override_manager.py`)**

**Responsabilidades:**
- Gestionar autorizaciones de override humano
- Registrar justificaciones y operadores
- Mantener audit trail de overrides

**Flujo de override:**
```
1. Detectar compliance_status == "NO_GO"
2. Verificar si human-override está habilitado
3. Validar presencia de operator-id y justification
4. Registrar override en compliance_report
5. Permitir continuación del proceso con advertencias
```

---

### **5. CAPA DE SALIDA (Output Layer)**

**Componentes:**

#### **5.1 JSON Generator (`liquidator/output/json_generator.py`)**

**Responsabilidades:**
- Generar JSON estructurado con todos los cálculos
- Incluir metadatos y compliance_report
- Calcular hashes para auditoría

**Estructura del JSON de salida:**
```json
{
  "meta": {
    "modo": "PERIÓDICA",
    "fecha_generacion": "2025-11-16T12:00:00",
    "fecha_corte": "2025-11-15",
    "fecha_ingreso": "2024-11-16",
    "moneda": "COP",
    "params_version": "2025-10-31",
    "input_hash": "sha256:...",
    "output_hash": "sha256:...",
    "generator_version": "1.0.0"
  },
  "trabajador": {
    "nombre": "",
    "documento": "",
    "tipo_contrato": "indefinido",
    "reside_en_lugar_trabajo": true
  },
  "parametros": {
    "SMMLV": 1423500,
    "AUXILIO_TRANS": 200000,
    "LIMITE_AUXILIO": 2847000,
    "TASA_INT_CESANTIAS": 0.12,
    "DIAS_BASE": 360,
    "TOPE_INDEMNIZACION_SMMLV": 20,
    "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01"
  },
  "desglose": {
    "SBL_GENERAL": 2200000,
    "SBL_VACACIONES": 2000000,
    "cesantias": {
      "valor": 2200000,
      "dias_liquidados": 360,
      "plazo_pago_legal": "2026-02-14",
      "norma": "Art.249-250 CST"
    },
    "intereses_cesantias": {
      "valor": 264000,
      "dias_liquidados": 360,
      "plazo_pago_legal": "2026-01-31",
      "norma": "Ley 50/1990 Art.99"
    },
    "prima": {
      "valor": 1100000,
      "dias_liquidados": 180,
      "plazo_pago_legal": "2025-12-31",
      "norma": "Art.306-308 CST"
    },
    "vacaciones": {
      "valor": 0,
      "dias_liquidados": 0,
      "norma": "Arts.186-192 CST",
      "nota": "No aplica en modo PERIÓDICA"
    }
  },
  "total_liquidacion_periodica": 3564000,
  "validaciones_y_alertas": {
    "auxilio_transporte_excluido": "Residencia en el lugar de trabajo (Finca).",
    "auxilio_conectividad_advertencia": "Verificar si está pactado como parte del salario habitual.",
    "recargo_dominical_aplicado": "No aplica (periodo anterior a 2025-07-01)."
  },
  "normas_aplicadas": [
    "Art.249-250 CST",
    "Ley 50/1990 Art.99",
    "Art.306-308 CST",
    "Art.65 CST",
    "Art.64 CST",
    "Art.192 CST",
    "Ley 2466/2025"
  ],
  "compliance_report": {
    "compliance_status": "GO",
    "summary": {
      "passed": 25,
      "warnings": 3,
      "failures": 0
    },
    "checks": [
      {
        "id": "V001",
        "description": "Parametros oficiales 2025 presentes y consistentes",
        "result": "PASS",
        "evidence": "SMMLV=1423500 matches params/2025.json",
        "rule_ref": ["Decreto 1572/2024"]
      }
      // ... más checks
    ],
    "blocking_failures": [],
    "params_version": "2025-10-31",
    "timestamp": "2025-11-02T07:25:00-05:00",
    "input_hash": "sha256:...",
    "output_hash": "sha256:...",
    "operator_action": {
      "action": "auto",
      "operator_id": null,
      "justification": null
    }
  }
}
```

#### **5.2 Markdown Generator (`liquidator/output/markdown_generator.py`)**

**Responsabilidades:**
- Generar documento Markdown legible para humanos
- Usar plantillas predefinidas
- Incluir todos los elementos legales requeridos

**Plantilla base (templates/comprobante_periodica.md):**
```markdown
# LIQUIDACIÓN PERIÓDICA DE PRESTACIONES SOCIALES
## Colombia - Año {año}

**Fecha de generación:** {fecha}
**Modo de liquidación:** {modo}
**Período liquidado:** {fecha_ingreso} a {fecha_corte}

### DATOS DEL TRABAJADOR
- **Nombre:** {nombre}
- **Documento:** {documento}
- **Tipo de contrato:** {tipo_contrato}
- **Reside en lugar de trabajo:** {reside_en_lugar}

### DETALLE DE PRESTACIONES

| Concepto | Valor (COP) | Días | Plazo de pago | Base legal |
|----------|-------------|------|---------------|------------|
| Cesantías | ${cesantias} | {dias_ces} | {plazo_ces} | {norma_ces} |
| Intereses | ${intereses} | {dias_int} | {plazo_int} | {norma_int} |
| Prima | ${prima} | {dias_prima} | {plazo_prima} | {norma_prima} |

### TOTAL LIQUIDACIÓN PERIÓDICA
**${total} COP**

### OBSERVACIONES
{observaciones}

### PLAZOS LEGALES DE PAGO
{plazos_detallados}

### DECLARACIÓN LEGAL
{declaracion}

---
**Firmas:**
Trabajador: ________________  Empleador: ________________
```

#### **5.3 PDF Generator (`liquidator/output/pdf_generator.py`)**

**Responsabilidades:**
- Convertir Markdown a PDF
- Aplicar estilos CSS profesionales
- Incluir encabezados y pies de página

**Dependencias:**
- `weasyprint` para conversión HTML→PDF
- `markdown` para conversión MD→HTML
- CSS personalizado en `templates/styles/pdf_styles.css`

---

### **6. CAPA DE AUDITORÍA (Audit Layer)**

**Componentes:**

#### **6.1 Audit Logger (`liquidator/audit/audit_logger.py`)**

**Responsabilidades:**
- Registrar todos los eventos de ejecución
- Mantener log estructurado por sesión
- Incluir timestamps y contexto

**Formato de log:**
```json
{
  "session_id": "uuid",
  "timestamp": "2025-11-16T12:00:00",
  "event_type": "calculation_started",
  "input_hash": "sha256:...",
  "params_version": "2025-10-31",
  "user_context": {
    "operator_id": null,
    "override_used": false
  }
}
```

#### **6.2 Hash Calculator (`liquidator/audit/hash_calculator.py`)**

**Responsabilidades:**
- Calcular hashes SHA256 de inputs y outputs
- Garantizar reproducibilidad de cálculos
- Permitir verificación posterior

#### **6.3 Trail Generator (`liquidator/audit/trail_generator.py`)**

**Responsabilidades:**
- Generar audit trail completo por ejecución
- Incluir inputs, outputs, compliance_report
- Almacenar en `audit/trails/` con timestamp

---

### **7. CAPA DE UTILIDADES (Utils Layer)**

**Componentes clave:**

#### **7.1 Date Utils (`liquidator/utils/date_utils.py`)**
- Cálculo de días entre fechas
- Determinación de semestres
- Validación de fechas legales
- Manejo de años bisiestos

#### **7.2 Currency Utils (`liquidator/utils/currency_utils.py`)**
- Formateo de moneda colombiana
- Redondeo según parámetros
- Conversión de valores

#### **7.3 Error Handler (`liquidator/utils/error_handler.py`)**
- Manejo centralizado de excepciones
- Mensajes de error informativos
- Logging de errores

---

## **FLUJO DE EJECUCIÓN COMPLETO**

```
1. CLI Entry Point (bin/liquidar)
   ↓
2. Input Parser
   ├─ Parsear flags/JSON
   ├─ Validar esquema
   └─ Normalizar datos
   ↓
3. Params Loader
   ├─ Cargar parámetros 2025
   ├─ Cargar normas
   └─ Cargar plazos
   ↓
4. Validators
   ├─ Validar contrato
   ├─ Validar fechas
   └─ Validar salarios
   ↓
5. Calculators
   ├─ Calcular SBLs
   ├─ Calcular prestaciones
   └─ Aplicar fórmulas legales
   ↓
6. Compliance Engine
   ├─ Ejecutar checklist
   ├─ Evaluar reglas
   ├─ Generar compliance_report
   └─ Determinar GO/NO_GO
   ↓
7. Decision Point
   ├─ Si NO_GO y enforce-compliance:
   │  ├─ Verificar human-override
   │  └─ Abortar o continuar con advertencias
   └─ Si GO: continuar
   ↓
8. Output Generators
   ├─ Generar JSON estructurado
   ├─ Generar Markdown
   └─ Generar PDF (opcional)
   ↓
9. Audit Trail
   ├─ Registrar ejecución
   ├─ Calcular hashes
   └─ Guardar trail completo
   ↓
10. CLI Output
    ├─ Mostrar resumen en consola
    └─ Indicar rutas de archivos generados
```

---

## **CASOS DE USO ESPECÍFICOS A SOPORTAR**

### **Caso 1: Trabajador de Finca Rural**
**Características:**
- `reside_en_lugar_trabajo = True`
- Auxilio de transporte NO aplica
- Puede tener auxilio de conectividad
- SBL_VACACIONES excluye auxilios

**Validaciones específicas:**
- V003: Verificar exclusión de auxilio de transporte
- Alerta sobre auxilio de conectividad

### **Caso 2: Salario Variable**
**Características:**
- Comisiones mensuales variables
- Horas extras fluctuantes
- Requiere promedio de últimos 12 meses

**Cálculos específicos:**
- Promedio de salarios históricos
- SBL basado en promedio
- Documentar periodo de promediación

### **Caso 3: Finiquito con Indemnización**
**Características:**
- Modo FINIQUITO
- Incluir vacaciones pendientes
- Calcular indemnización
- Aplicar tope 20 SMMLV

**Validaciones específicas:**
- Verificar tope de indemnización
- Validar pago inmediato (Art. 65 CST)
- Incluir salarios pendientes

### **Caso 4: Periodo Parcial de Semestre**
**Características:**
- Trabajador ingresa o sale a mitad de semestre
- Prima proporcional a días trabajados

**Cálculos específicos:**
- Determinar días exactos del semestre trabajado
- Calcular prima proporcional
- Validar que días no excedan 185

---

## **DEPENDENCIAS Y TECNOLOGÍAS**

### **Python Packages Requeridos:**
```
# Core
python >= 3.8

# CLI
argparse (built-in)
click (opcional, para CLI más avanzada)

# Data handling
jsonschema >= 4.19.0
pydantic >= 2.0.0 (validación de datos)
python-dateutil >= 2.8.0

# Output generation
markdown >= 3.4.0
weasyprint >= 59.0
jinja2 >= 3.1.0 (para templates)

# Hashing y seguridad
hashlib (built-in)

# Testing
pytest >= 7.4.0
pytest-cov >= 4.1.0

# Logging
loguru >= 0.7.0

# YAML (para configs)
pyyaml >= 6.0
```

### **Herramientas de Desarrollo:**
```
# Linting
black >= 23.0.0
flake8 >= 6.0.0
mypy >= 1.5.0

# Documentation
sphinx >= 7.0.0
sphinx-rtd-theme >= 1.3.0
```

---

## **ESTRATEGIA DE TESTING**

### **Niveles de Testing:**

**1. Unit Tests**
- Cada calculator individual
- Cada validator individual
- Cada compliance rule

**2. Integration Tests**
- Flujo completo periódica
- Flujo completo finiquito
- Casos de borde

**3. Compliance Tests**
- Validar cada regla del checklist
- Verificar bloqueos correctos
- Probar overrides

**4. End-to-End Tests**
- Ejecutar con ejemplos reales
- Verificar outputs completos
- Validar PDFs generados

### **Coverage Target:**
- Mínimo 85% de cobertura de código
- 100% en módulos de compliance
- 100% en calculators críticos

---

## **CONFIGURACIÓN Y DEPLOYMENT**

### **config/default_config.yaml:**
```yaml
system:
  version: "1.0.0"
  environment: "production"
  
params:
  year: 2025
  auto_update: false
  
compliance:
  enforce_by_default: true
  default_policy: "standard"
  allow_overrides: true
  
output:
  default_format: "json"
  generate_pdf: true
  pdf_style: "default"
  
audit:
  enabled: true
  log_level: "INFO"
  retention_days: 365
  
security:
  hash_algorithm: "sha256"
  encrypt_sensitive: false
```

---

## **ROADMAP DE IMPLEMENTACIÓN**

### **Fase 1: Fundación (Semana 1-2)**
1. Estructura de directorios
2. Archivos de parámetros legales
3. Módulos de params y legal
4. Validadores básicos

### **Fase 2: Calculadores (Semana 3-4)**
1. SBL Calculator completo
2. Prestaciones Calculator
3. Vacaciones Calculator
4. Tests unitarios de calculadores

### **Fase 3: Compliance (Semana 5-6)**
1. Compliance Engine
2. Checklist Loader
3. Rule Evaluator
4. Override Manager
5. Tests de compliance

### **Fase 4: Output (Semana 7)**
1. JSON Generator
2. Markdown Generator
3. PDF Generator
4. Templates

### **Fase 5: CLI y Auditoría (Semana 8)**
1. CLI principal
2. Audit Logger
3. Hash Calculator
4. Trail Generator

### **Fase 6: Testing y Documentación (Semana 9-10)**
1. Suite completa de tests
2. Documentación técnica
3. Guías de usuario
4. Ejemplos completos

---

## **PRÓXIMOS PASOS INMEDIATOS**

Para la siguiente sesión de trabajo, necesitaremos implementar en orden:

1. **Primero:** Archivos de parámetros legales (`params/2025.json`, `params/normas.json`)
2. **Segundo:** Módulo de parámetros (`liquidator/params/params_loader.py`)
3. **Tercero:** Calculadores base (`liquidator/calculators/sbl_calculator.py`)
4. **Cuarto:** Motor de compliance (`liquidator/compliance/compliance_engine.py`)
5. **Quinto:** Generadores de salida (`liquidator/output/`)

¿Deseas que comencemos con la implementación de alguno de estos componentes en particular?
# Plan de Implementación Secuencial por Sesiones
## Sistema de Liquidación de Nómina Colombia 2025

---

## **SESIÓN 1: Fundamentos y Parámetros Legales**
### Objetivo: Establecer la base legal y estructura de datos

### **Entregables:**

**1.1 Estructura de Directorios Completa**
```bash
# Crear toda la estructura de carpetas
liquidacion_cli/
├── bin/
├── liquidator/{core,calculators,validators,compliance,legal,params,output,audit,utils,tests}/
├── params/
├── legal_docs/
├── templates/
├── audit/
├── examples/
├── docs/
├── config/
└── scripts/
```

**1.2 Archivos de Parámetros Legales**
- `params/2025.json` - Parámetros oficiales completos
- `params/normas.json` - Referencias normativas detalladas
- `params/plazos.json` - Plazos legales de pago
- `params/schema.json` - Schema de validación

**1.3 Documentación Legal de Referencia**
- `legal_docs/CST_articulos_relevantes.md`
- `legal_docs/leyes_vigentes.md`
- `legal_docs/checklist_cumplimiento.md`

**1.4 Módulo de Parámetros**
- `liquidator/params/__init__.py`
- `liquidator/params/params_loader.py`
- `liquidator/params/params_validator.py`
- `liquidator/params/params_versioning.py`

**1.5 Tests Iniciales**
- `liquidator/tests/test_params/test_loader.py`
- `liquidator/tests/fixtures/params_test.json`

### **Criterios de Aceptación:**
✓ Todos los parámetros 2025 cargados correctamente  
✓ Validación de schema funcional  
✓ Tests de carga de parámetros pasando  
✓ Documentación legal accesible

---

## **SESIÓN 2: Módulos de Validación y Utilidades**
### Objetivo: Implementar validadores de entrada y utilidades base

### **Entregables:**

**2.1 Validadores de Entrada**
- `liquidator/validators/__init__.py`
- `liquidator/validators/input_validator.py`
  - Validación de schema JSON
  - Validación de tipos de datos
  - Validación de rangos
- `liquidator/validators/contract_validator.py`
  - Validación de tipos de contrato
  - Rechazo de prestación de servicios
- `liquidator/validators/date_validator.py`
  - Validación de formato de fechas
  - Validación de coherencia temporal
  - Validación de periodos
- `liquidator/validators/salary_validator.py`
  - Validación de componentes salariales
  - Validación de límites (ej. 2 SMMLV para auxilio)

**2.2 Utilidades Base**
- `liquidator/utils/__init__.py`
- `liquidator/utils/date_utils.py`
  - Cálculo de días entre fechas
  - Determinación de semestres
  - Manejo de años bisiestos
  - Cálculo de días hábiles
- `liquidator/utils/currency_utils.py`
  - Formateo de moneda COP
  - Redondeo según parámetros
  - Conversión de valores
- `liquidator/utils/file_utils.py`
  - Lectura/escritura de JSON
  - Manejo de paths
  - Validación de existencia de archivos
- `liquidator/utils/error_handler.py`
  - Excepciones personalizadas
  - Mensajes de error descriptivos
  - Logging de errores

**2.3 Tests de Validadores**
- `liquidator/tests/test_validators/`
  - `test_input_validator.py`
  - `test_contract_validator.py`
  - `test_date_validator.py`
  - `test_salary_validator.py`

**2.4 Tests de Utilidades**
- `liquidator/tests/test_utils/`
  - `test_date_utils.py`
  - `test_currency_utils.py`

### **Criterios de Aceptación:**
✓ Validadores rechazan inputs inválidos correctamente  
✓ Validadores aceptan inputs válidos  
✓ Utilidades de fecha calculan correctamente días  
✓ Utilidades de moneda formatean correctamente  
✓ Tests de validadores y utilidades pasando  
✓ Coverage > 90% en validadores

---

## **SESIÓN 3: Módulo Legal y Gestión de Normas**
### Objetivo: Implementar gestión de referencias legales y plazos

### **Entregables:**

**3.1 Repositorio de Normas**
- `liquidator/legal/__init__.py`
- `liquidator/legal/normas_repository.py`
  - Carga de normas desde JSON
  - Búsqueda de normas por ID
  - Obtención de texto relevante
  - Obtención de URLs de referencia

**3.2 Gestión de Plazos Legales**
- `liquidator/legal/plazos_manager.py`
  - Cálculo de fechas límite de pago
  - Determinación de plazos según concepto
  - Manejo de plazos inmediatos (finiquito)
  - Validación de fechas de pago

**3.3 Gestión de Topes y Límites**
- `liquidator/legal/topes_manager.py`
  - Aplicación de tope 20 SMMLV para indemnización
  - Validación de límite 2 SMMLV para auxilio
  - Cálculo de topes variables

**3.4 Gestión de Recargos**
- `liquidator/legal/recargos_manager.py`
  - Recargo dominical (80% desde 2025-07-01)
  - Recargos nocturnos
  - Recargos festivos
  - Validación de fechas de aplicación

**3.5 Tests del Módulo Legal**
- `liquidator/tests/test_legal/`
  - `test_normas_repository.py`
  - `test_plazos_manager.py`
  - `test_topes_manager.py`
  - `test_recargos_manager.py`

### **Criterios de Aceptación:**
✓ Normas se cargan y consultan correctamente  
✓ Plazos se calculan según normativa  
✓ Topes se aplican correctamente  
✓ Recargo dominical se aplica solo desde 2025-07-01  
✓ Tests del módulo legal pasando  
✓ Coverage > 85%

---

## **SESIÓN 4: Calculador de SBL (Salario Base de Liquidación)**
### Objetivo: Implementar cálculo correcto de SBL en sus variantes

### **Entregables:**

**4.1 Calculador de SBL**
- `liquidator/calculators/__init__.py`
- `liquidator/calculators/sbl_calculator.py`
  - `calculate_sbl_general()`
    - Salario base + comisiones + extras + bonificaciones
    - Inclusión condicional de auxilio conectividad
  - `calculate_sbl_vacaciones()`
    - Salario base + comisiones
    - Exclusión de extras, recargos y auxilios
  - `calculate_sbl_prima()`
    - Similar a SBL_GENERAL o con reglas específicas
  - `apply_auxilio_rules()`
    - Verificación de residencia en lugar de trabajo
    - Verificación de límite 2 SMMLV
    - Generación de alertas
  - `calculate_promedio_variable()`
    - Promedio de últimos 12 meses
    - Manejo de periodos incompletos

**4.2 Casos Especiales de SBL**
- Trabajador de finca rural (sin auxilio transporte)
- Salario variable (promediación)
- Auxilio de conectividad (validación de pacto)
- Múltiples componentes salariales

**4.3 Tests del Calculador de SBL**
- `liquidator/tests/test_calculators/test_sbl.py`
  - Test caso finca rural
  - Test salario variable
  - Test auxilio conectividad
  - Test límites de auxilio
  - Test exclusiones correctas

**4.4 Fixtures de Datos de Prueba**
- `liquidator/tests/fixtures/sbl_cases.json`
  - Casos de prueba con resultados esperados

### **Criterios de Aceptación:**
✓ SBL_GENERAL calcula correctamente todos los componentes  
✓ SBL_VACACIONES excluye extras y auxilios  
✓ Auxilio de transporte se excluye en finca rural  
✓ Límite de 2 SMMLV se valida correctamente  
✓ Salarios variables promedian correctamente  
✓ Tests pasando con casos reales  
✓ Coverage > 95% (módulo crítico)

---

## **SESIÓN 5: Calculadores de Prestaciones Sociales**
### Objetivo: Implementar cálculo de cesantías, intereses y prima

### **Entregables:**

**5.1 Calculador de Prestaciones**
- `liquidator/calculators/prestaciones_calculator.py`
  - `calculate_dias_servicio()`
    - Cálculo de días entre fechas
    - Inclusión del día de corte
  - `calculate_cesantias()`
    - Fórmula: (SBL_GENERAL × días) / 360
    - Redondeo según parámetros
  - `calculate_intereses_cesantias()`
    - Fórmula: (cesantías × días × 0.12) / 360
    - Validación de tasa 12%
  - `calculate_dias_prima()`
    - Determinación de semestre
    - Cálculo de días trabajados en semestre
  - `calculate_prima()`
    - Fórmula: (SBL_PRIMA × días_prima) / 360
    - Proporcionalidad correcta

**5.2 Validaciones de Fórmulas**
- Verificación de base 360 días
- Validación de resultados contra casos conocidos
- Manejo de redondeos

**5.3 Tests de Prestaciones**
- `liquidator/tests/test_calculators/test_prestaciones.py`
  - Test cesantías año completo
  - Test cesantías periodo parcial
  - Test intereses correctos
  - Test prima semestre completo
  - Test prima periodo parcial
  - Test casos de borde (1 día, 365 días, etc.)

**5.4 Casos de Prueba Documentados**
- Ejemplo finca rural (360 días)
- Ejemplo periodo parcial
- Ejemplo con salario variable

### **Criterios de Aceptación:**
✓ Cesantías calculan correctamente con base 360  
✓ Intereses usan tasa 12% anual  
✓ Prima es proporcional al semestre trabajado  
✓ Cálculos coinciden con ejemplos legales  
✓ Tests pasando con múltiples casos  
✓ Coverage > 95% (módulo crítico)

---

## **SESIÓN 6: Calculadores de Vacaciones e Indemnización**
### Objetivo: Completar calculadores para modo FINIQUITO

### **Entregables:**

**6.1 Calculador de Vacaciones**
- `liquidator/calculators/vacaciones_calculator.py`
  - `calculate_dias_vacaciones_causadas()`
    - Cálculo según tiempo de servicio
  - `calculate_valor_vacaciones()`
    - Fórmula: (SBL_VACACIONES × días) / 720
    - Uso de SBL_VACACIONES (sin extras)
  - `determinar_compensacion_dinero()`
    - Solo en modo FINIQUITO
    - Validación de días pendientes

**6.2 Calculador de Indemnización**
- `liquidator/calculators/indemnizacion_calculator.py`
  - `calculate_indemnizacion_sin_justa_causa()`
    - Diferenciación por tipo de contrato
    - Aplicación de fórmulas según tiempo de servicio
  - `apply_tope_20_smmlv()`
    - Limitación según Art. 64 CST
  - `calculate_salario_pendiente()`
    - Días adeudados × salario diario

**6.3 Tests de Vacaciones e Indemnización**
- `liquidator/tests/test_calculators/test_vacaciones.py`
  - Test cálculo de días causados
  - Test valor con base 720
  - Test exclusión en modo PERIÓDICA
- `liquidator/tests/test_calculators/test_indemnizacion.py`
  - Test indemnización contrato indefinido
  - Test indemnización término fijo
  - Test aplicación de tope 20 SMMLV
  - Test salario pendiente

### **Criterios de Aceptación:**
✓ Vacaciones calculan con base 720  
✓ Vacaciones se excluyen en modo PERIÓDICA  
✓ Indemnización aplica tope 20 SMMLV  
✓ Indemnización diferencia tipos de contrato  
✓ Tests pasando para ambos modos  
✓ Coverage > 90%

---

## **SESIÓN 7: Motor de Cumplimiento Legal - Parte 1**
### Objetivo: Implementar checklist y evaluación de reglas

### **Entregables:**

**7.1 Checklist Loader**
- `liquidator/compliance/__init__.py`
- `liquidator/compliance/checklist_loader.py`
  - Carga de CHECKLIST desde markdown/JSON
  - Parseo de reglas
  - Conversión a objetos ejecutables
  - Categorización por severidad

**7.2 Rule Evaluator**
- `liquidator/compliance/rule_evaluator.py`
  - Clase base `ComplianceRule`
  - Implementación de reglas individuales:
    - **V001:** Parámetros oficiales 2025
    - **V002:** Contrato válido
    - **V003:** Auxilio transporte correcto
    - **V004:** Fórmulas de cesantías correctas
    - **V005:** Intereses tasa 12%
  - Método `evaluate()` que retorna PASS/WARN/FAIL
  - Recolección de evidencia

**7.3 Implementación de Reglas Críticas**
- Cada regla como clase independiente
- Método de evaluación específico
- Generación de evidencia detallada

**7.4 Tests de Compliance - Parte 1**
- `liquidator/tests/test_compliance/test_checklist_loader.py`
- `liquidator/tests/test_compliance/test_rule_evaluator.py`
- `liquidator/tests/test_compliance/test_individual_rules.py`
  - Test V001-V005 individualmente

### **Criterios de Aceptación:**
✓ Checklist se carga correctamente  
✓ Reglas se parsean a objetos ejecutables  
✓ Cada regla V001-V005 evalúa correctamente  
✓ Evidencia se genera apropiadamente  
✓ Tests de reglas individuales pasando  
✓ Coverage > 90%

---

## **SESIÓN 8: Motor de Cumplimiento Legal - Parte 2**
### Objetivo: Completar todas las reglas y sistema de reportes

### **Entregables:**

**8.1 Implementación de Reglas Restantes**
- Implementar reglas V006-V010:
  - **V006:** Prima semestre proporcional
  - **V007:** Vacaciones excluidas en periódica
  - **V008:** Plazos de pago documentados
  - **V009:** Sustento legal presente
  - **V010:** Hashes y versionamiento

**8.2 Compliance Engine**
- `liquidator/compliance/compliance_engine.py`
  - Orquestación de todas las validaciones
  - Ejecución secuencial de reglas
  - Agregación de resultados
  - Determinación de estado final (GO/NO_GO)
  - Identificación de fallos bloqueantes

**8.3 Report Generator**
- `liquidator/compliance/report_generator.py`
  - Generación de `compliance_report` estructurado
  - Resumen de resultados (passed/warnings/failures)
  - Listado detallado de checks
  - Identificación de blocking_failures
  - Inclusión de timestamps y hashes

**8.4 Tests de Compliance - Parte 2**
- `liquidator/tests/test_compliance/test_compliance_engine.py`
- `liquidator/tests/test_compliance/test_report_generator.py`
- Tests de integración de compliance completo

### **Criterios de Aceptación:**
✓ Todas las reglas V001-V010 implementadas  
✓ Compliance Engine orquesta correctamente  
✓ Estado GO/NO_GO se determina correctamente  
✓ Reporte de cumplimiento completo y estructurado  
✓ Tests de integración pasando  
✓ Coverage > 95% (módulo crítico)

---

## **SESIÓN 9: Sistema de Override y Auditoría**
### Objetivo: Implementar overrides humanos y sistema de auditoría

### **Entregables:**

**9.1 Override Manager**
- `liquidator/compliance/override_manager.py`
  - Validación de permisos de override
  - Registro de operator_id y justificación
  - Actualización de compliance_report
  - Validación de campos requeridos
  - Generación de alertas de override

**9.2 Audit Logger**
- `liquidator/audit/__init__.py`
- `liquidator/audit/audit_logger.py`
  - Registro de eventos de ejecución
  - Logging estructurado por sesión
  - Timestamps y contexto completo
  - Niveles de log (INFO, WARN, ERROR)

**9.3 Hash Calculator**
- `liquidator/audit/hash_calculator.py`
  - Cálculo de SHA256 de inputs
  - Cálculo de SHA256 de outputs
  - Serialización determinística para hashing
  - Verificación de integridad

**9.4 Trail Generator**
- `liquidator/audit/trail_generator.py`
  - Generación de audit trail completo
  - Inclusión de inputs, outputs, compliance_report
  - Almacenamiento en `audit/trails/`
  - Formato JSON estructurado con timestamp

**9.5 Versioning Manager**
- `liquidator/audit/versioning_manager.py`
  - Control de versiones de parámetros
  - Control de versiones del generador
  - Trazabilidad de cambios

**9.6 Tests de Override y Auditoría**
- `liquidator/tests/test_compliance/test_override.py`
- `liquidator/tests/test_audit/test_audit_logger.py`
- `liquidator/tests/test_audit/test_hash_calculator.py`
- `liquidator/tests/test_audit/test_trail_generator.py`

### **Criterios de Aceptación:**
✓ Overrides requieren operator_id y justificación  
✓ Overrides se registran en compliance_report  
✓ Audit trail completo se genera por ejecución  
✓ Hashes garantizan integridad  
✓ Logs estructurados y completos  
✓ Tests pasando  
✓ Coverage > 85%

---

## **SESIÓN 10: Motor Principal de Orquestación**
### Objetivo: Implementar el motor que coordina todo el flujo

### **Entregables:**

**10.1 Input Parser**
- `liquidator/core/__init__.py`
- `liquidator/core/input_parser.py`
  - Parseo de argumentos CLI
  - Parseo de archivos JSON
  - Normalización de datos
  - Aplicación de defaults
  - Validación de campos requeridos

**10.2 Workflow Orchestrator**
- `liquidator/core/workflow_orchestrator.py`
  - Orquestación de flujo PERIÓDICA
  - Orquestación de flujo FINIQUITO
  - Manejo de diferencias entre modos
  - Control de flujo según compliance

**10.3 Engine Principal**
- `liquidator/core/engine.py`
  - Clase `LiquidacionEngine`
  - Método `process_input()`
  - Método `run_compliance_check()`
  - Método `generate_output()`
  - Integración de todos los módulos
  - Manejo de errores centralizado

**10.4 Tests de Integración del Motor**
- `liquidator/tests/test_core/test_input_parser.py`
- `liquidator/tests/test_core/test_workflow_orchestrator.py`
- `liquidator/tests/test_core/test_engine.py`

**10.5 Pseudocódigo Documentado**
```python
# Flujo completo documentado
def process_liquidacion(input_data):
    # 1. Cargar parámetros
    # 2. Validar entrada
    # 3. Calcular SBLs
    # 4. Calcular prestaciones
    # 5. Ejecutar compliance
    # 6. Decidir GO/NO_GO
    # 7. Generar outputs
    # 8. Registrar auditoría
```

### **Criterios de Aceptación:**
✓ Motor orquesta correctamente todos los módulos  
✓ Flujos PERIÓDICA y FINIQUITO funcionan  
✓ Compliance se ejecuta en el momento correcto  
✓ Errores se manejan apropiadamente  
✓ Tests de integración pasando  
✓ Coverage > 90%

---

## **SESIÓN 11: Generadores de Salida - JSON y Markdown**
### Objetivo: Implementar generación de documentos

### **Entregables:**

**11.1 JSON Generator**
- `liquidator/output/__init__.py`
- `liquidator/output/json_generator.py`
  - Generación de JSON estructurado completo
  - Inclusión de meta, trabajador, parametros
  - Inclusión de desglose detallado
  - Inclusión de compliance_report
  - Cálculo de hashes
  - Validación de schema de salida

**11.2 Template Manager**
- `liquidator/output/template_manager.py`
  - Carga de plantillas Markdown
  - Sustitución de variables
  - Manejo de condicionales
  - Renderizado de tablas

**11.3 Markdown Generator**
- `liquidator/output/markdown_generator.py`
  - Generación de comprobante legible
  - Uso de plantillas
  - Formateo de moneda
  - Inclusión de firmas
  - Inclusión de plazos legales
  - Inclusión de declaración legal

**11.4 Plantillas de Documentos**
- `templates/comprobante_periodica.md`
- `templates/comprobante_finiquito.md`
- `templates/partials/header.md`
- `templates/partials/footer.md`
- `templates/partials/firmas.md`

**11.5 Tests de Generadores**
- `liquidator/tests/test_output/test_json_generator.py`
- `liquidator/tests/test_output/test_markdown_generator.py`
- `liquidator/tests/test_output/test_template_manager.py`

### **Criterios de Aceptación:**
✓ JSON generado cumple schema definido  
✓ JSON incluye todos los campos requeridos  
✓ Markdown es legible y profesional  
✓ Plantillas se renderizan correctamente  
✓ Moneda se formatea apropiadamente  
✓ Tests pasando  
✓ Coverage > 85%

---

## **SESIÓN 12: Generador de PDF y Estilos**
### Objetivo: Implementar generación de PDF profesional

### **Entregables:**

**12.1 PDF Generator**
- `liquidator/output/pdf_generator.py`
  - Conversión de Markdown a HTML
  - Conversión de HTML a PDF (weasyprint)
  - Aplicación de estilos CSS
  - Manejo de páginas múltiples
  - Inclusión de encabezados y pies de página
  - Manejo de errores de generación

**12.2 Estilos CSS**
- `templates/styles/pdf_styles.css`
  - Estilos profesionales para PDF
  - Formato de tablas
  - Formato de encabezados
  - Formato de firmas
  - Márgenes y espaciado
  - Colores corporativos

**12.3 Recursos Adicionales**
- Logo (si aplica)
- Fuentes personalizadas (opcional)

**12.4 Tests de PDF Generator**
- `liquidator/tests/test_output/test_pdf_generator.py`
  - Test generación básica
  - Test con casos complejos
  - Test manejo de errores

**12.5 Validación Visual**
- Ejemplos de PDF generados
- Revisión de formato
- Validación de legibilidad

### **Criterios de Aceptación:**
✓ PDF se genera correctamente desde Markdown  
✓ Estilos CSS se aplican apropiadamente  
✓ PDF es profesional y legible  
✓ Tablas se formatean correctamente  
✓ Firmas y declaraciones incluidas  
✓ Tests pasando  
✓ PDFs de ejemplo validados visualmente

---

## **SESIÓN 13: CLI Principal y Argumentos**
### Objetivo: Implementar interfaz de línea de comandos completa

### **Entregables:**

**13.1 Script CLI Principal**
- `bin/liquidar` (script ejecutable)
  - Shebang y permisos
  - Importación del motor
  - Llamada a función principal

**13.2 Parseo de Argumentos**
- Implementación completa de argparse
- Todos los flags definidos:
  - `--modo`, `--fecha_ingreso`, `--fecha_corte`
  - `--salario_mensual`, `--comisiones_promedio_mensual`
  - `--horas_extras_promedio_mensual`, `--bonificaciones_promedio_mensual`
  - `--reside_en_lugar_trabajo`, `--auxilio_conectividad`
  - `--dias_vacaciones_pendientes`, `--tipo_contrato`
  - `--enforce-compliance`, `--compliance-policy`
  - `--human-override`, `--operator-id`, `--override-reason`
  - `--input`, `--output`
  - `--test-run`, `--generate-pdf`, `--compliance-check-only`

**13.3 Modos Especiales**
- Modo `--test-run`: ejecuta suite de tests
- Modo `--generate-pdf`: genera PDF desde JSON existente
- Modo `--compliance-check-only`: solo validación

**13.4 Output en Consola**
- Mensajes informativos
- Resumen de resultados
- Indicación de archivos generados
- Manejo de errores user-friendly

**13.5 Función Main**
```python
def main():
    # Parsear argumentos
    # Cargar input
    # Ejecutar motor
    # Manejar compliance
    # Generar outputs
    # Mostrar resumen
```

**13.6 Tests de CLI**
- `liquidator/tests/test_cli/test_argument_parsing.py`
- `liquidator/tests/test_cli/test_main_flow.py`
- Tests de modos especiales

### **Criterios de Aceptación:**
✓ CLI acepta todos los argumentos definidos  
✓ Argumentos se parsean correctamente  
✓ Archivo JSON de entrada se carga correctamente  
✓ Modos especiales funcionan  
✓ Output en consola es claro e informativo  
✓ Errores se muestran de forma comprensible  
✓ Tests de CLI pasando

---

## **SESIÓN 14: Ejemplos y Casos de Prueba Reales**
### Objetivo: Crear ejemplos completos y casos de prueba documentados

### **Entregables:**

**14.1 Ejemplos de Entrada**
- `examples/example_finca_rural.json`
  - Caso específico de trabajador de finca
  - `reside_en_lugar_trabajo = true`
  - Sin auxilio de transporte
  - Con auxilio de conectividad
- `examples/example_salario_variable.json`
  - Salarios históricos variables
  - Comisiones fluctuantes
  - Promediación de 12 meses
- `examples/example_finiquito.json`
  - Modo FINIQUITO completo
  - Vacaciones pendientes
  - Indemnización incluida
- `examples/example_periodo_parcial.json`
  - Ingreso a mitad de semestre
  - Prima proporcional

**14.2 Documentación de Ejemplos**
- `examples/README_examples.md`
  - Explicación de cada ejemplo
  - Resultados esperados
  - Comandos para ejecutar

**14.3 Casos de Borde**
- `liquidator/tests/fixtures/edge_cases/`
  - Contrato de 1 día
  - Contrato de 365 días (año bisiesto)
  - Salario exactamente 2 SMMLV
  - Múltiples componentes salariales
  - Periodo que cruza 2025-07-01 (recargo dominical)

**14.4 Tests de Integración End-to-End**
- `liquidator/tests/test_integration/test_periodica.py`
  - Test completo con ejemplo finca rural
  - Verificación de todos los cálculos
  - Verificación de compliance
- `liquidator/tests/test_integration/test_finiquito.py`
  - Test completo de finiquito
  - Verificación de indemnización
- `liquidator/tests/test_integration/test_edge_cases.py`
  - Test de todos los casos de borde

**14.5 Scripts de Validación**
- `scripts/validate_examples.py`
  - Script que ejecuta todos los ejemplos
  - Verifica que outputs sean correctos
  - Compara contra resultados esperados

### **Criterios de Aceptación:**
✓ Todos los ejemplos ejecutan correctamente  
✓ Resultados coinciden con cálculos manuales  
✓ Casos de borde manejados apropiadamente  
✓ Tests end-to-end pasando  
✓ Documentación de ejemplos clara  
✓ Coverage general > 85%

---

## **SESIÓN 15: Documentación Técnica Completa**
### Objetivo: Documentar todo el sistema exhaustivamente

### **Entregables:**

**15.1 Documentación de Arquitectura**
- `docs/architecture.md`
  - Diagrama de componentes
  - Flujo de datos
  - Decisiones de diseño
  - Patrones utilizados

**15.2 Referencia de API Interna**
- `docs/api_reference.md`
  - Documentación de cada módulo
  - Documentación de clases principales
  - Documentación de métodos públicos
  - Ejemplos de uso

**15.3 Documentación de Cumplimiento Legal**
- `docs/legal_compliance.md`
  - Explicación del checklist
  - Mapeo de reglas a normas
  - Justificación de validaciones
  - Referencias legales completas

**15.4 Guía de Usuario**
- `docs/user_guide.md`
  - Instalación
  - Uso básico
  - Ejemplos paso a paso
  - Preguntas frecuentes
  - Troubleshooting

**15.5 Guía para Desarrolladores**
- `docs/developer_guide.md`
  - Setup del entorno de desarrollo
  - Estructura del código
  - Cómo agregar nuevas validaciones
  - Cómo agregar nuevos calculadores
  - Cómo ejecutar tests
  - Cómo contribuir

**15.6 README Principal**
- `README.md`
  - Descripción del proyecto
  - Características principales
  - Instalación rápida
  - Ejemplo de uso
  - Links a documentación completa
  - Licencia

**15.7 Documentación de Configuración**
- `docs/configuration.md`
  - Explicación de config/default_config.yaml
  - Personalización de parámetros
  - Políticas de cumplimiento
  - Configuración de logging

### **Criterios de Aceptación:**
✓ Toda la arquitectura documentada  
✓ API interna documentada  
✓ Cumplimiento legal explicado  
✓ Guías de usuario y desarrollador completas  
✓ README claro y conciso  
✓ Ejemplos en documentación funcionan

---

## **SESIÓN 16: Configuración y Scripts Auxiliares**
### Objetivo: Implementar sistema de configuración y herramientas auxiliares

### **Entregables:**

**16.1 Archivos de Configuración**
- `config/default_config.yaml`
  - Configuración del sistema
  - Configuración de compliance
  - Configuración de output
  - Configuración de audit
- `config/compliance_policies.yaml`
  - Política lenient
  - Política standard
  - Política strict
- `config/logging_config.yaml`
  - Niveles de log
  - Formatos de log
  - Destinos de log

**16.2 Script de Actualización de Parámetros**
- `scripts/update_params.py`
  - Script para actualizar parámetros anuales
  - Validación de nuevos parámetros
  - Backup de parámetros anteriores
  - Documentación de cambios

**16.3 Script de Validación de Cumplimiento**
- `scripts/validate_compliance.py`
  - Validador independiente
  - Puede ejecutarse sin calcular liquidación
  - Genera reporte detallado

**16.4 Script de Generación de Datos de Prueba**
- `scripts/generate_test_data.py`
  - Genera casos de prueba aleatorios
  - Genera casos de borde automáticamente
  - Útil para testing exhaustivo

**16.5 Setup de Instalación**
- `setup.py`
  - Configuración de instalación con pip
  - Definición de dependencias
  - Entry points para CLI
  - Metadatos del paquete

**16.6 Archivos de Dependencias**
- `requirements.txt`
  - Dependencias de producción
- `requirements-dev.txt`
  - Dependencias de desarrollo y testing

**16.7 Configuración de Testing**
- `pytest.ini`
  - Configuración de pytest
  - Paths de tests
  - Opciones de coverage

### **Criterios de Aceptación:**
✓ Configuraciones cargan correctamente  
✓ Scripts auxiliares funcionan  
✓ setup.py permite instalación con pip  
✓ Dependencias documentadas  
✓ pytest configurado correctamente

---

## **SESIÓN 17: Testing Exhaustivo y Coverage**
### Objetivo: Alcanzar coverage objetivo y testing completo

### **Entregables:**

**17.1 Completar Suite de Tests Unitarios**
- Revisar coverage de cada módulo
- Agregar tests faltantes
- Alcanzar mínimo 85% coverage general
- Alcanzar 95%+ en módulos críticos:
  - calculators
  - compliance
  - validators

**17.2 Tests de Integración Completos**
- Tests de flujo completo PERIÓDICA
- Tests de flujo completo FINIQUITO
- Tests de transiciones entre estados
- Tests de manejo de errores

**17.3 Tests de Regresión**
- Comparación contra casos conocidos
- Verificación de cálculos exactos
- Validación contra ejemplos legales

**17.4 Tests de Performance**
- Medición de tiempos de ejecución
- Identificación de cuellos de botella
- Optimización si es necesario

**17.5 Reporte de Coverage**
- Generación de reporte HTML
- Identificación de áreas sin cobertura
- Plan de acción para mejorar coverage

**17.6 Documentación de Tests**
- Explicación de estrategia de testing
- Documentación de fixtures
- Guía para ejecutar tests

### **Criterios de Aceptación:**
✓ Coverage general > 85%  
✓ Coverage módulos críticos > 95%  
✓ Todos los tests pasando  
✓ Tests de regresión validados  
✓ Performance aceptable  
✓ Documentación de tests completa

---

## **SESIÓN 18: Validación Legal y Compliance Final**
### Objetivo: Validación exhaustiva del cumplimiento legal

### **Entregables:**

**18.1 Revisión Completa del Checklist**
- Verificar implementación de cada regla V001-V010
- Validar evidencia generada por cada regla
- Confirmar referencias normativas correctas

**18.2 Validación de Cálculos contra Normativa**
- Cesantías: Art. 249-250 CST
- Intereses: Ley 50/1990 Art. 99
- Prima: Art. 306-308 CST
- Vacaciones: Arts. 186-192 CST
- Indemnización: Art. 64 CST
- Plazos: Art. 65 CST

**18.3 Validación de Casos Especiales**
- Finca rural sin auxilio transporte
- Salario variable con promediación
- Recargo dominical 80% desde 2025-07-01
- Tope 20 SMMLV para indemnización

**18.4 Documentación de Cumplimiento**
- Reporte de validación legal completo
- Mapeo detallado norma → implementación
- Evidencia de cumplimiento por cada artículo

**18.5 Revisión de Audit Trail**
- Verificar trazabilidad completa
- Confirmar hashes y versionamiento
- Validar reproducibilidad

**18.6 Casos de Prueba Legales**
- Ejecutar todos los ejemplos
- Comparar contra cálculos manuales
- Validar con contador o abogado laboral (recomendado)

### **Criterios de Aceptación:**
✓ Todas las reglas del checklist implementadas  
✓ Cálculos coinciden con normativa  
✓ Casos especiales manejados correctamente  
✓ Documentación de cumplimiento completa  
✓ Audit trail funcional  
✓ Validación externa realizada (opcional pero recomendado)

---

## **SESIÓN 19: Optimización y Refactoring**
### Objetivo: Optimizar código y mejorar calidad

### **Entregables:**

**19.1 Análisis de Código**
- Ejecutar linters (black, flake8, mypy)
- Identificar code smells
- Identificar duplicación de código

**19.2 Refactoring**
- Eliminar duplicación
- Mejorar nombres de variables/funciones
- Simplificar lógica compleja
- Aplicar patrones de diseño donde corresponda

**19.3 Optimización de Performance**
- Optimizar cálculos repetitivos
- Cachear resultados cuando sea apropiado
- Optimizar lectura de archivos

**19.4 Mejoras de Mantenibilidad**
- Agregar docstrings faltantes
- Mejorar comentarios
- Simplificar interfaces

**19.5 Type Hints**
- Agregar type hints completos
- Ejecutar mypy para verificación de tipos

**19.6 Reporte de Calidad**
- Métricas de código
- Complejidad ciclomática
- Índice de mantenibilidad

### **Criterios de Aceptación:**
✓ Linters pasan sin errores  
✓ Type hints completos  
✓ Duplicación minimizada  
✓ Performance aceptable  
✓ Código más legible y mantenible  
✓ Documentación actualizada

---

## **SESIÓN 20: Preparación para Producción y Release**
### Objetivo: Preparar el sistema para uso en producción

### **Entregables:**

**20.1 Configuración de Producción**
- Configuración optimizada para producción
- Manejo de secretos (si aplica)
- Configuración de logging para producción

**20.2 Documentación de Deployment**
- Guía de instalación en servidor
- Requisitos de sistema
- Configuración de permisos
- Backup y recuperación

**20.3 Herramientas de Monitoreo**
- Logging estructurado
- Métricas de uso
- Alertas de errores

**20.4 Seguridad**
- Revisión de seguridad
- Manejo de datos sensibles
- Validación de inputs
- Protección contra inyección

**20.5 Versionamiento**
- Definir versión inicial (1.0.0)
- Estrategia de versionamiento semántico
- Changelog inicial

**20.6 Licencia y Legal**
- Definir licencia (MIT recomendada)
- Archivo LICENSE
- Disclaimer legal

**20.7 Empaquetado**
- Crear paquete distribuible
- Publicar en PyPI (opcional)
- Crear release en GitHub

**20.8 Documentación Final**
- README final pulido
- Guía de instalación final
- Notas de release

**20.9 Validación Final**
- Ejecutar suite completa de tests
- Validar todos los ejemplos
- Verificar documentación

**20.10 Plan de Mantenimiento**
- Proceso de actualización de parámetros anuales
- Proceso de actualización de normas
- Plan de soporte

### **Criterios de Aceptación:**
✓ Sistema listo para producción  
✓ Documentación completa y actualizada  
✓ Todos los tests pasando  
✓ Seguridad validada  
✓ Paquete distribuible creado  
✓ Plan de mantenimiento definido  
✓ Release 1.0.0 lista

---

## **RESUMEN DE ENTREGABLES POR SESIÓN**

| Sesión | Tema Principal | Entregables Clave |
|--------|----------------|-------------------|
| 1 | Fundamentos y Parámetros | Estructura, params/*.json, params_loader.py |
| 2 | Validadores y Utilidades | validators/, utils/, tests básicos |
| 3 | Módulo Legal | legal/, normas_repository.py, plazos_manager.py |
| 4 | Calculador SBL | sbl_calculator.py, tests de SBL |
| 5 | Prestaciones Sociales | prestaciones_calculator.py, tests |
| 6 | Vacaciones e Indemnización | vacaciones_calculator.py, indemnizacion_calculator.py |
| 7 | Compliance Parte 1 | checklist_loader.py, rule_evaluator.py, V001-V005 |
| 8 | Compliance Parte 2 | V006-V010, compliance_engine.py, report_generator.py |
| 9 | Override y Auditoría | override_manager.py, audit/, hash_calculator.py |
| 10 | Motor Principal | core/engine.py, workflow_orchestrator.py |
| 11 | Output JSON y Markdown | json_generator.py, markdown_generator.py, templates/ |
| 12 | PDF Generator | pdf_generator.py, pdf_styles.css |
| 13 | CLI Principal | bin/liquidar, argparse completo |
| 14 | Ejemplos y Casos Reales | examples/, tests de integración |
| 15 | Documentación Técnica | docs/, README.md |
| 16 | Configuración y Scripts | config/, scripts/ |
| 17 | Testing Exhaustivo | Coverage >85%, tests completos |
| 18 | Validación Legal | Validación compliance, casos legales |
| 19 | Optimización | Refactoring, performance, calidad |
| 20 | Release | Producción, deployment, release 1.0.0 |

---

## **MÉTRICAS DE ÉXITO FINAL**

Al completar las 20 sesiones, el sistema debe cumplir:

✓ **Funcionalidad Completa:**
- Modo PERIÓDICA funcional
- Modo FINIQUITO funcional
- Todos los calculadores implementados
- Sistema de compliance completo

✓ **Calidad de Código:**
- Coverage general > 85%
- Coverage módulos críticos > 95%
- Linters pasando sin errores
- Type hints completos

✓ **Cumplimiento Legal:**
- Todas las reglas V001-V010 implementadas
- Cálculos validados contra normativa
- Audit trail completo
- Referencias legales documentadas

✓ **Documentación:**
- README completo
- Guías de usuario y desarrollador
- API documentada
- Ejemplos funcionales

✓ **Producción:**
- Sistema instalable con pip
- CLI funcional
- Outputs correctos (JSON, MD, PDF)
- Configuración de producción

---

## **RECOMENDACIONES PARA LA EJECUCIÓN**

1. **Seguir el orden secuencial:** Cada sesión construye sobre la anterior
2. **Validar entregables:** Verificar criterios de aceptación antes de avanzar
3. **Mantener tests actualizados:** Ejecutar tests después de cada cambio
4. **Documentar mientras se desarrolla:** No dejar documentación para el final
5. **Revisar compliance regularmente:** Validar contra checklist en cada sesión relevante
6. **Hacer commits frecuentes:** Control de versiones desde el inicio
7. **Solicitar revisiones:** Especialmente en módulos de compliance y cálculos

---

