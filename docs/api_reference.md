# Referencia de API Interna
## Sistema de Liquidación de Nómina Colombia 2025

### Versión: 1.0.0
### Fecha: 2025-11-04

---

## Tabla de Contenidos

1. [API Core](#1-api-core)
2. [Módulo Calculators](#2-módulo-calculators)
3. [Módulo Validators](#3-módulo-validators)
4. [Módulo Compliance](#4-módulo-compliance)
5. [Módulo Legal](#5-módulo-legal)
6. [Módulo Params](#6-módulo-params)
7. [Módulo Output](#7-módulo-output)
8. [Módulo Utils](#8-módulo-utils)
9. [Módulo Audit](#9-módulo-audit)

---

## 1. API Core

### 1.1 LiquidacionEngine

Clase principal que orquesta el flujo completo de liquidación.

#### Constructor
```python
LiquidacionEngine() -> LiquidacionEngine
```

#### Métodos
```python
process(input_data: Dict) -> Dict
```
Orquesta el proceso completo de liquidación desde inputs hasta outputs.

**Parámetros:**
- `input_data` (Dict): Datos de entrada como se especifica en [schema_referencia.json](../params/schema.json).

**Retorna:**
- `Dict`: Resultado completo con estructura definida en [schema_output.json](../params/schema.json).

**Ejemplo:**
```python
from liquidator.core.engine import LiquidacionEngine

engine = LiquidacionEngine()
result = engine.process({
    "modo": "PERIODICA",
    "fecha_ingreso": "2024-11-16",
    "fecha_corte": "2025-11-15",
    "salario_mensual": 2000000,
    "reside_en_lugar_trabajo": True,
    "auxilio_conectividad": 200000
})
```

```python
compliance_check(input_data: Dict) -> Dict
```
Ejecuta únicamente las validaciones de compliance sin generar liquidación completa.

**Retorna:**
- `Dict`: Reporte de cumplimiento con estado GO/NO_GO.

```python
validate_input(input_data: Dict) -> bool
```
Realiza validaciones básicas de estructura y valores de entrada.

**Retorna:**
- `bool`: True si la entrada es válida.

**Lanza:**
- `ValidationError`: Si la entrada es inválida.

---

### 1.2 InputParser

Parser y normalizador de datos de entrada.

#### Constructor
```python
InputParser() -> InputParser
```

#### Métodos
```python
parse_cli_args(args: argparse.Namespace) -> Dict
```
Convierte argumentos de CLI a estructura interna.

**Parámetros:**
- `args` (argparse.Namespace): Argumentos parseados por argparse.

**Retorna:**
- `Dict`: Estructura interna normalizada.

```python
parse_json_file(file_path: str) -> Dict
```
Parsea y valida archivo JSON de entrada.

**Parámetros:**
- `file_path` (str): Ruta al archivo JSON.

**Retorna:**
- `Dict`: Datos parseados y validados.

**Lanza:**
- `FileNotFoundError`: Si el archivo no existe.
- `FileParsingError`: Si el JSON es inválido.

---

### 1.3 WorkflowOrchestrator

Gestiona flujos específicos según modo de liquidación.

#### Constructor
```python
WorkflowOrchestrator() -> WorkflowOrchestrator
```

#### Métodos
```python
execute_periodica_workflow(input_data: Dict, params: Dict) -> Dict
```
Ejecuta flujo específico para liquidación periódica.

**Retorna:**
- `Dict`: Resultado de cálculos periódicos (sin vacaciones ni indemnización).

```python
execute_finiquito_workflow(input_data: Dict, params: Dict) -> Dict
```
Ejecuta flujo específico para liquidación de finiquito.

**Retorna:**
- `Dict`: Resultado completo incluyendo vacaciones e indemnización.

---

## 2. Módulo Calculators

### 2.1 SBLCalculator

Calculador de Salario Base de Liquidación en sus variantes.

#### Constructor
```python
SBLCalculator(params: Dict) -> SBLCalculator
```

#### Métodos
```python
calculate_sbl_general(input_data: Dict) -> float
```
Calcula SBL para cesantías, intereses y prima.

**Fórmula:** `salario_mensual + comisiones_promedio_mensual + horas_extras_promedio_mensual + bonificaciones_promedio_mensual [+ auxilio]`

**Retorna:**
- `float`: SBL_GENERAL calculado.

```python
calculate_sbl_vacaciones(input_data: Dict) -> float
```
Calcula SBL para vacaciones (excluye extras y auxilios).

**Fórmula:** `salario_mensual + comisiones_promedio_mensual`

**Retorna:**
- `float`: SBL_VACACIONES calculado.

```python
apply_auxilio_rules(sbl: float, input_data: Dict, params: Dict) -> float
```
Aplica reglas específicas de auxilio de transporte/conectividad.

**Retorna:**
- `float`: SBL ajustado según reglas.

```python
calculate_promedio_variable(salarios_historicos: List[Dict]) -> float
```
Calcula promedio de salarios variables últimos 12 meses.

**Parámetros:**
- `salarios_historicos` (List[Dict]): Lista de salarios históricos.

**Retorna:**
- `float`: Promedio calculado.

---

### 2.2 PrestacionesCalculator

Calculador de prestaciones sociales principales.

#### Constructor
```python
PrestacionesCalculator(params: Dict) -> PrestacionesCalculator
```

#### Métodos
```python
calculate_dias_servicio(fecha_ingreso: str, fecha_corte: str) -> int
```
Calcula días de servicio laborado.

**Retorna:**
- `int`: Días calculados incluyendo día de corte.

```python
calculate_cesantias(sbl_general: float, dias_servicio: int) -> Dict[str, Any]
```
Calcula cesantías según normativas Art. 249-250 CST.

**Fórmula:** `(SBL_GENERAL × días_servicio) / 360`

**Retorna:**
- `Dict`: Estructura con valor, días liquidados, norma y plazo.

```python
calculate_intereses_cesantias(cesantias_valor: float, dias_servicio: int) -> Dict[str, Any]
```
Calcula intereses sobre cesantías según Ley 50/1990 Art.99.

**Fórmula:** `(cesantías × días_servicio × 0.12) / 360`

**Retorna:**
- `Dict`: Estructura con valor, tasa aplicada, norma y plazo.

```python
calculate_prima(sbl_prima: float, dias_semestre: int) -> Dict[str, Any]
```
Calcula prima de servicios proporcional al semestre según Art. 306-308 CST.

**Retorna:**
- `Dict`: Estructura con valor, días liquidados, norma y plazo.

```python
calculate_all(input_data: Dict, sbls: Dict[str, float]) -> Dict[str, Dict]
```
Calcula todas las prestaciones en una sola llamada.

**Retorna:**
- `Dict`: Diccionario con cesantías, intereses, prima y sus detalles.

---

### 2.3 VacacionesCalculator

Calculador de vacaciones y compensación.

#### Constructor
```python
VacacionesCalculator(params: Dict) -> VacacionesCalculator
```

#### Métodos
```python
calculate_dias_causados(fecha_ingreso: str, fecha_corte: str) -> int
```
Calcula días de vacaciones causadas según Art. 186 CST.

**Regla:** 15 días laborados = 1 día de vacaciones.

**Retorna:**
- `int`: Días causados.

```python
calculate_valor_vacaciones(sbl_vacaciones: float, dias_vacaciones: int) -> Dict[str, Any]
```
Calcula valor monetario de vacaciones.

**Fórmula:** `(SBL_VACACIONES × días_vacaciones) / 720`

**Retorna:**
- `Dict`: Valor calculado y detalles.

```python
determinar_compensacion_dinero(modo: str, dias_pendientes: int) -> bool
```
Determina si aplica compensación en dinero.

**Regla:** Solo en modo FINIQUITO con días pendientes > 0.

---

### 2.4 IndemnizacionCalculator

Calculador de indemnizaciones por terminación de contrato.

#### Constructor
```python
IndemnizacionCalculator(params: Dict) -> IndemnizacionCalculator
```

#### Métodos
```python
calculate_indemnizacion_sin_justa_causa(input_data: Dict, sbl_general: float) -> Dict[str, Any]
```
Calcula indemnización por terminación sin justa causa.

**Retorna:**
- `Dict`: Valor calculado con aplicación de tope si aplica.

```python
apply_tope_20_smmlv(sbl: float, params: Dict) -> float
```
Aplica tope máximo de 20 SMMLV según Art. 64 CST.

**Retorna:**
- `float`: SBL con tope aplicado si es necesario.

```python
calculate_salario_pendiente(salario_diario: float, dias_salario_pendiente: int) -> float
```
Calcula salario adeudado pendiente de pago.

---

## 3. Módulo Validators

### 3.1 InputValidator

Validador de estructura y valores básicos de entrada.

#### Constructor
```python
InputValidator() -> InputValidator
```

#### Métodos
```python
validate(input_data: Dict) -> bool
```
Valida estructura y valores de entrada.

**Lanza:**
- `ValidationError`: Si hay errores de validación.

```python
validate_required_fields(input_data: Dict) -> None
```
Verifica presencia de campos obligatorios.

```python
validate_date_format(input_data: Dict) -> None
```
Valida formato y coherencia de fechas.

```python
validate_salary_ranges(input_data: Dict) -> None
```
Valida rangos salariales mínimos y máximos.
---

### 3.2 ContractValidator

Validador específico para tipos de contrato.

#### Constructor
```python
ContractValidator() -> ContractValidator
```

#### Métodos
```python
validate_contract_type(contract_type: str) -> bool
```
Valida tipo de contrato según normativa.

**Lanza:**
- `ComplianceError`: Para contratos no liquidables (prestación de servicios).

```python
validate_termination_reason(motivo: str, modo: str) -> bool
```
Valida motivo de terminación según contexto.

---

### 3.3 DateValidator

Validador de fechas y periodos.

#### Constructor
```python
DateValidator() -> DateValidator
```

#### Métodos
```python
validate_date_range(fecha_inicio: str, fecha_fin: str) -> bool
```
Valida que fecha_fin sea posterior a fecha_inicio.

```python
validate_business_days(fecha_inicio: str, fecha_fin: str) -> int
```
Verifica que existan mínimo 1 día laborable entre fechas.

```python
calculate_months_between(fecha_inicio: str, fecha_fin: str) -> int
```
Calcula meses completos entre dos fechas.

---

### 3.4 SalaryValidator

Validador de componentes salariales.

#### Constructor
```python
SalaryValidator(params: Dict) -> SalaryValidator
```

#### Métodos
```python
validate_auxilio_transport_limit(sbl: float, params: Dict) -> bool
```
Valida límite de 2 SMMLV para auxilio de transporte.

```python
validate_minimum_wage(salario_mensual: float, params: Dict) -> bool
```
Valida salario mínimo legal vigente.

```python
validate_commission_limits(comisiones: float, salario_base: float) -> bool
```
Valida límites de comisiones sobre base salarial.

---

## 4. Módulo Compliance

### 4.1 ComplianceEngine

Motor principal de validación de cumplimiento legal.

#### Constructor
```python
ComplianceEngine() -> ComplianceEngine
```

#### Métodos
```python
run_validations(input_data: Dict, sbls: Dict, prestaciones: Dict, params: Dict) -> Dict
```
Ejecuta todas las validaciones de cumplimiento V001-V010.

**Retorna:**
- `Dict`: Reporte completo con estado y resultados individuales.

```python
determine_status(validation_results: List[Dict]) -> str
```
Determina estado final GO/WARN/NO_GO basado en resultados.

```python
handle_blocking_failure(report: Dict, input_data: Dict) -> Dict
```
Maneja fallos bloqueantes según política de compliance.

---

### 4.2 ChecklistLoader

Carga y parsea checklist de cumplimiento legal.

#### Constructor
```python
ChecklistLoader() -> ChecklistLoader
```

#### Métodos
```python
load_checklist() -> Dict[str, Dict]
```
Carga checklist desde archivo JSON.

**Retorna:**
- `Dict`: Estructura completar de reglas by ID.

```python
parse_rule(rule_data: Dict) -> ComplianceRule
```
Convierte datos de regla a objeto ejecutable.

---

### 4.3 RuleEvaluator

Evaluador individual de reglas de compliance.

#### Constructor
```python
RuleEvaluator() -> RuleEvaluator
```

#### Métodos
```python
evaluate(rule_id: str, input_data: Dict, sbls: Dict, prestaciones: Dict, params: Dict) -> Dict
```
Ejecuta evaluación de regla específica según ID.

**Retorna:**
- `Dict`: Resultado con PASS/WARN/FAIL y evidencia.

```python
evaluate_v001_params_oficiales(rule_id: str, params: Dict) -> Dict
```
Valida V001: Parámetros oficiales 2025.

```python
evaluate_v002_contrato_valido(rule_id: str, input_data: Dict) -> Dict
```
Valida V002: Contrato válido (no prestación de servicios).

```python
evaluate_v003_auxilio_transporte(rule_id: str, input_data: Dict, sbls: Dict) -> Dict
```
Valida V003: Auxilio transporte aplicado correctamente.

[... y así para V004-V010]

---

### 4.4 ReportGenerator

Generador de reportes de cumplimiento estructurados.

#### Constructor
```python
ReportGenerator() -> ReportGenerator
```

#### Métodos
```python
create_report(validation_results: List[Dict], compliance_status: str) -> Dict
```
Crea reporte completo con resumen y detalles.

```python
generate_summary(validation_results: List[Dict]) -> Dict
```
Genera resumen cuantitativo (passed/warnings/failures).

```python
identify_blocking_failures(validation_results: List[Dict]) -> List[Dict]
```
Identifica fallos que bloquean ejecución.

---

## 5. Módulo Legal

### 5.1 NormasRepository

Repositorio de normas legales y referentes normativos.

#### Constructor
```python
NormasRepository() -> NormasRepository
```

#### Métodos
```python
get_norma(nombre: str) -> Dict[str, Any]
```
Obtiene información completa de una norma por nombre.

```python
get_norma_text(norma_id: str) -> str
```
Obtiene texto relevante de una norma específica.

```python
search_by_keyword(keyword: str) -> List[Dict[str, str]]
```
Busca normas por palabra clave en descripción o nombre.

```python
get_reference_url(norma_id: str) -> str
```
Obtiene URL de referencia normativa si está disponible.

---

### 5.2 PlazosManager

Gestor de plazos legales de pago.

#### Constructor
```python
PlazosManager() -> PlazosManager
```

#### Métodos
```python
get_plazo_pago(concepto: str, params: Dict) -> Dict[str, str]
```
Obtiene plazo legal de pago por concepto.

**Retorna:**
- `Dict`: Con fecha límite y descripción.

```python
calculate_fecha_limite(concepto: str, referencia_date: str) -> str
```
Calcula fecha límite específica basada en fecha de referencia.

```python
validate_plazo_cumplido(concepto: str, fecha_pago: str) -> bool
```
Valida si pago se realizó dentro del plazo legal.

---

### 5.3 TopesManager

Gestor de topes y límites legales.

#### Constructor
```python
TopesManager(params: Dict) -> TopesManager
```

#### Métodos
```python
apply_tope_indemnizacion(sbl: float) -> float
```
Aplica tope de 20 SMMLV a indemnización.

```python
validate_tope_auxilio_transporte(sbl: float) -> bool
```
Valida si SBL está dentro de límite para auxilio transporte.

```python
calculate_tope_maximo(tipo: str, params: Dict) -> float
```
Calcula valor de tope por tipo (indemnización, auxilio, etc.).

---

### 5.4 RecargosManager

Gestor de recargos legales.

#### Constructor
```python
RecargosManager(params: Dict) -> RecargosManager
```

#### Métodos
```python
apply_recargo_dominical(valor_horas: float, fecha_trabajo: str) -> float
```
Aplica recargo dominical del 80% desde 2025-07-01.

```python
validate_aplicacion_recargo(fecha_trabajo: str) -> bool
```
Valida si aplica recargo según fecha de trabajo.

```python
calculate_recargo_nocturno(valor_hora: str) -> float
```
Calcula recargo nocturno (35% sobre valor hora).

---

## 6. Módulo Params

### 6.1 ParamsLoader

Cargador de parámetros legales oficiales.

#### Constructor
```python
ParamsLoader() -> ParamsLoader
```

#### Métodos
```python
load_params(anio: int = 2025) -> Dict[str, Any]
```
Carga parámetros del año especificado desde params/{anio}.json.

```python
validate_schema(params: Dict) -> bool
```
Valida estructura de parámetros contra schema.

```python
get_version_info(anio: int) -> Dict[str, str]
```
Obtiene información de versión referencia de parámetros.

---

### 6.2 ParamsValidator

Validador de parámetros legales.

#### Constructor
```python
ParamsValidator() -> ParamsValidator
```

#### Métodos
```python
validate_required_params(params: Dict) -> bool
```
Valida presencia de parámetros obligatorios.

```python
validate_param_ranges(params: Dict) -> bool
```
Valida rangos y valores de parámetros.

```python
validate_normative_consistency(params: Dict) -> bool
```
Valida consistencia normativa (ej. auxilio ≤ 2 SMMLV).

---

### 6.3 ParamsVersioning

Control de versiones de parámetros para trazabilidad.

#### Constructor
```python
ParamsVersioning() -> ParamsVersioning
```

#### Métodos
```python
get_current_version(params: Dict) -> str
```
Obtiene versión actual de parámetros.

```python
compare_versions(version1: str, version2: str) -> str
```
Compara dos versiones y retorna: 'greater', 'equal', 'lower'.

```python
get_changes_between_versions(version1: str, version2: str) -> List[str]
```
Obtiene lista de cambios entre versiones.

```python
validate_version_compatibility(required_version: str, current_version: str) -> bool
```
Valida compatibilidad entre versiones.

---

## 7. Módulo Output

### 7.1 JSONGenerator

Generador de salida JSON estructurada.

#### Constructor
```python
JSONGenerator() -> JSONGenerator
```

#### Métodos
```python
generate(input_data: Dict, sbls: Dict, prestaciones: Dict, compliance: Dict) -> Dict
```
Genera JSON completo con estructura definida.

```python
validate_output_schema(output_data: Dict) -> bool
```
Valida JSON de salida contra schema de validación.

```python
calculate_output_hash(output_data: Dict) -> str
```
Calcula hash SHA256 del JSON para integridad.

---

### 7.2 MarkdownGenerator

Generador de documentos Markdown legibles.

#### Constructor
```python
MarkdownGenerator() -> MarkdownGenerator
```

#### Métodos
```python
generar_comprobante(liquidacion_data: Dict, modo: str) -> str
```
Genera comprobante en formato Markdown.

```python
renderizar_detalle_prestaciones(prestaciones: Dict) -> str
```
Renderiza tabla de detalle de prestaciones.

```python
renderizar_plazos_legales(prestaciones: Dict) -> str
```
Renderiza sección de plazos legales de pago.

---

### 7.3 PDFGenerator

Generador de PDF profesionales desde Markdown.

#### Constructor
```python
PDFGenerator() -> PDFGenerator
```

#### Métodos
```python
generate_from_markdown(markdown_content: str, output_path: str) -> bool
```
Genera PDF desde contenido Markdown.

```python
apply_company_branding(html_content: str) -> str
```
Aplica branding y estilos corporativos al contenido HTML.

```python
add_headers_footers(html_content: str) -> str
```
Añade encabezados y pies de página al documento.

---

### 7.4 TemplateManager

Gestor de plantillas para various outputs.

#### Constructor
```python
TemplateManager() -> TemplateManager
```

#### Métodos
```python
load_template(template_name: str) -> str
```
Carga plantilla desde directorio templates/.

```python
render_template(template: str, context: Dict) -> str
```
Renderiza plantilla con contexto específico.

```python
get_available_templates() -> List[str]
```
Retorna lista de plantillas disponibles.

---

## 8. Módulo Utils

### 8.1 DateUtils

Utilidades de manejo de fechas y periodos.

#### Métodos estáticos
```python
days_between(fecha_inicio: str, fecha_fin: str) -> int
```
Calcula días entre fechas incluyendo día final.

```python
calculate_semester(fecha: str) -> Tuple[str, str, str]
```
Determina semestre y fechas límite de prima para una fecha dada.

```python
is_leap_year(anio: int) -> bool
```
Determina si año es bisiesto.

```python
add_business_days(fecha: str, dias: int) -> str
```
Añade días hábiles a fecha determinada.

---

### 8.2 CurrencyUtils

Utilidades de formato y operaciones monetarias.

#### Métodos estáticos
```python
format_currency(amount: float, currency: str = 'COP') -> str
```
Formatea monto con separadores y símbolo de moneda.

```python
round_to_nearest(amount: float, nearest: int = 0) -> int
```
Redondea monto al valor más cercano especificado.

```python
validate_amount_range(amount: float, min_amount: float, max_amount: float) -> bool
```
Valida que monto esté dentro de rango permitido.

---

### 8.3 FileUtils

Utilidades de manejo de archivos.

#### Métodos estáticos
```python
read_json_file(file_path: str) -> Dict
```
Lee y parsea archivo JSON con manejo seguro de errores y encoding.

```python
write_json_file(file_path: str, data: Dict, pretty_print: bool = True) -> bool
```
Escribe datos a archivo JSON con formato y encoding UTF-8.

```python
ensure_directory_exists(dir_path: str) -> bool
```
Asegura que directorio exista, creándolo si es necesario.

```python
backup_file(file_path: str) -> str
```
Crea backup de archivo con timestamp.

---

### 8.4 ErrorHandler

Manejo centralizado de excepciones.

#### Constructor
```python
ErrorHandler(log_level: str = 'INFO') -> ErrorHandler
```

#### Métodos
```python
handle_error(error: Exception, context: Dict) -> Dict
```
Maneja error según tipo y contexto, retornando estructura standard.

```python
log_error(error: Exception, context: Dict) -> None
```
Registra error en sistema de logs.

```python
create_error_response(error: Exception) -> Dict
```
Crea respuesta de error user-friendly para CLI.

---

## 9. Módulo Audit

### 9.1 AuditLogger

Registrador de eventos de auditoría.

#### Constructor
```python
AuditLogger() -> AuditLogger
```

#### Métodos
```python
log_session_start(session_data: Dict) -> str
```
Registra inicio de sesión de ejecución.

```python
log_calculation_event(event_type: str, details: Dict) -> None
```
Registra evento específico de cálculo.

```python
log_session_end(session_id: str, results: Dict) -> None
```
Registra fin de sesión con resultados.

```python
get_session_logs(session_id: str) -> List[Dict]
```
Obtiene logs de sesión específica.

---

### 9.2 HashCalculator

Calculador de hashes para integridad de datos.

#### Constructor
```python
HashCalculator(algorithm: str = 'SHA256') -> HashCalculator
```

#### Métodos
```python
calculate(data: Union[Dict, str, bytes]) -> str
```
Calcula hash de datos especificados.

```python
calculate_file_hash(file_path: str) -> str
```
Calcula hash de archivo completo.

```python
verify_integrity(original_hash: str, data: Any) -> bool
```
Verifica integridad comparando hashes.

---

### 9.3 TrailGenerator

Generador de audit trail completo por ejecución.

#### Constructor
```python
TrailGenerator() -> TrailGenerator
```

#### Métodos
```python
generate_full_trail(input_data: Dict, output_data: Dict, compliance_report: Dict) -> str
```
Genera trail completo y guarda en audit/trails/.

```python
generate_minimal_trail(session_id: str, summary: Dict) -> None
```
Genera trail minimal con solo resumen de ejecución.

```python
get_trail(session_id: str) -> Dict
```
Recupera trail completo de sesión específica.

---

### 9.4 VersioningManager

Gestor de versiones para trazabilidad de cálculos.

#### Constructor
```python
VersioningManager() -> VersioningManager
```

#### Métodos
```python
register_calculation_version(input_hash: str, params_version: str, engine_version: str) -> str
```
Registra versión de cálculo específico.

```python
validate_reproducibility(session_id: str, new_input: Dict) -> bool
```
Valida que cálculo sea reproducible con mismos inputs.

```python
get_version_history(params_version: str) -> List[Dict]
```
Obtiene historial de cambios por versión.

---

## 10. Estructuras de Datos Comunes

### 10.1 InputData

Estructura estándar para datos de entrada:

```python
{
    "modo": str,                    # "PERIODICA" | "FINIQUITO"
    "fecha_ingreso": str,           # "YYYY-MM-DD"
    "fecha_corte": str,             # "YYYY-MM-DD"
    "salario_mensual": int,         # COP
    "salarios_historicos": List[Dict],
    "comisiones_promedio_mensual": float,
    "horas_extras_promedio_mensual": float,
    "bonificaciones_promedio_mensual": float,
    "reside_en_lugar_trabajo": bool,
    "auxilio_conectividad": int,    # COP
    "dias_vacaciones_pendientes": int,
    "tipo_contrato": str,           # "indefinido" | "fijo"
    "motivo_terminacion": str,      # solo FINIQUITO
    "enforce-compliance": bool,     # default: true
    "compliance-policy": str,       # "lenient" | "standard" | "strict"
    "human-override": bool,
    "operator-id": str,
    "override-reason": str
}
```

### 10.2 OutputData

Estructura estándar para datos de salida:

```python
{
    "meta": {
        "modo": str,
        "fecha_generacion": str,
        "params_version": str,
        "generator_version": str
    },
    "trabajador": {...},
    "parametros": {...},
    "desglose": {
        "SBL_GENERAL": float,
        "SBL_VACACIONES": float,
        "cesantias": {...},
        "intereses_cesantias": {...},
        "prima": {...},
        "vacaciones": {...},
        "indemnizacion": {...}
    },
    "compliance_report": {...}
}
```

### 10.3 ComplianceResult

Estructura para resultados de validación:

```python
{
    "id": str,                      # "V001", "V002", etc.
    "description": str,
    "result": str,                  # "PASS" | "WARN" | "FAIL"
    "evidence": List[str],
    "rule_ref": List[str],
    "details": str
}
```

---

## 11. Errores y Excepciones

### Jerarquía de Excepciones

```
LiquidacionError                    : Exception base de todas las excepciones del sistema
├─ ValidationError                  : Errores de validación de entrada
├─ ComplianceError                  : Errores de cumplimiento legal
├─ CalculationError                 : Errores en cálculos matemáticos
├─ FileError                        : Errores de manejo de archivos
├─ ParsingError                     : Errores de parseo de datos
└─ OutputGenerationError           : Errores en generación de outputs
```

### Uso Excepciones

```python
try:
    engine = LiquidacionEngine()
    result = engine.process(input_data)
except ValidationError as e:
    print(f"Error de validación: {e}")
    sys.exit(1)
except ComplianceError as e:
    print(f"Error de cumplimiento legal: {e}")
    sys.exit(2)
except Exception as e:
    print(f"Error inesperado: {e}")
    sys.exit(3)
```

---

## 12. Ejemplos de Uso

### 12.1 Liquidación Periódica Básica

```python
from liquidator.core.engine import LiquidacionEngine
from liquidator.utils.currency_utils import format_currency

input_data = {
    "modo": "PERIODICA",
    "fecha_ingreso": "2024-11-16",
    "fecha_corte": "2025-11-15",
    "salario_mensual": 2000000,
    "reside_en_lugar_trabajo": True,
    "auxilio_conectividad": 200000,
    "enforce-compliance": True
}

engine = LiquidacionEngine()
result = engine.process(input_data)

print(f"Monto total de liquidación: {format_currency(result['desglose']['cesantias']['valor'])}")
print(f"Estado de cumplimiento: {result['compliance_report']['compliance_status']}")
```

### 12.2 Validación de Compliance Únicamente

```python
from liquidator.core.engine import LiquidacionEngine

engine = LiquidacionEngine()
compliance_result = engine.compliance_check(input_data)

print(f"Validaciones pasadas: {compliance_result['summary']['passed']}")
print(f"Warnings: {compliance_result['summary']['warnings']}")
print(f"Fallas: {compliance_result['summary']['failures']}")
```

### 12.3 Uso Individual de Calculadoras

```python
from liquidator.params.params_loader import ParamsLoader
from liquidator.calculators.sbl_calculator import SBLCalculator
from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator

# Cargar parámetros
params = ParamsLoader().load_params(2025)

# Calcular SBL
sbl_calc = SBLCalculator(params)
sbl_general = sbl_calc.calculate_sbl_general(input_data)

# Calcular cesantías
prest_calc = PrestacionesCalculator(params)
cesantias = prest_calc.calculate_cesantias(sbl_general, 365)

print(f"Cesantías: {cesantias['valor']:,.0f} COP")
print(f"Norma aplicada: {cesantias['norma']}")
```

---

## 13. Testing

### 13.1 Tests de Unidades

```python
import pytest
from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator

def test_cesantias_calculation():
    params = {"DIAS_BASE": 360.0, "REDONDEO": 0}
    calc = PrestacionesCalculator(params)
    
    cesantias = calc.calculate_cesantias(2000000, 365)
    
    assert cesantias['valor'] == 20333333  # (2000000 * 365) / 360
    assert cesantias['norma'] == 'Art.249-250 CST'
```

### 13.2 Tests de Integración

```python
def test_full_periodica_workflow():
    engine = LiquidacionEngine()
    result = engine.process({
        "modo": "PERIODICA",
        "fecha_ingreso": "2024-01-01",
        "fecha_corte": "2024-12-31",
        "salario_mensual": 2000000,
        "reside_en_lugar_trabajo": False
    })
    
    assert result['meta']['modo'] == 'PERIÓDICA'
    assert result['desglose']['vacaciones']['valor'] == 0
    assert result['compliance_report']['compliance_status'] == 'GO'
```

---

## 14. Extensión y Personalización

### 14.1 Añadir Nueva Prestación

Para añadir nueva prestación:

1. Extender calculadora existente o añadir nueva
2. Añadir validación de compliance si aplica
3. Actualizar schema de output
4. Añadir tests unitarios y de integración

### 14.2 Añadir Nueva Regla de Compliance

Para añadir nueva regla:

1. Implementar método en RuleEvaluator
2. Añadir ID y descripción en VALIDATION_RULES
3. Actualizar checklist si aplica
4. Añadir tests específicos

---

## 15. Mejores Prácticas

1. **Siempre validar inputs** con InputValidator antes de procesar
2. **Manejar todas las excepciones** con ErrorHandler apropiado
3. **Verificar compliance status** antes de usar resultados
4. **Generar audit trails** para traceability legal
5. **Usar versioning_manager** para reprod
4. Usar params oficiales siempre
5. Mantener consistencia en estructuras de datos
6. Escribir tests para nuevos componentes siempre
7. Documentar cualquier cambio con razonamiento legal si aplica

---

**Nota:** Esta documentación permanecerá sincronizada con el código. Para cualquier cambio en la API, actualice esta referencia inmediatamente.
